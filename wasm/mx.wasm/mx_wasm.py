#
# Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
#
# The Universal Permissive License (UPL), Version 1.0
#
# Subject to the condition set forth below, permission is hereby granted to any
# person obtaining a copy of this software, associated documentation and/or
# data (collectively the "Software"), free of charge and under any and all
# copyright rights in the Software, and any and all patent rights owned or
# freely licensable by each licensor hereunder covering either (i) the
# unmodified Software as contributed to or provided by such licensor, or (ii)
# the Larger Works (as defined below), to deal in both
#
# (a) the Software, and
#
# (b) any piece of software and/or hardware listed in the lrgrwrks.txt file if
# one is included with the Software each a "Larger Work" to which the Software
# is contributed by such licensors),
#
# without restriction, including without limitation the rights to copy, create
# derivative works of, display, perform, and distribute the Software and make,
# use, sell, offer for sale, import, export, have made, and have sold the
# Software and the Larger Work(s), and to sublicense the foregoing rights on
# either these or other terms.
#
# This license is subject to the following condition:
#
# The above copyright notice and either this complete permission notice or at a
# minimum a reference to the UPL must be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import mx
import mx_wasm_benchmark  # pylint: disable=unused-import

import errno
import os

_suite = mx.suite('wasm')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class GraalWasmSourceProject(mx.NativeProject):
    def __init__(self, suite, name, deps, workingSets, subDir, results, output, **args):
        self.suite = suite
        self.name = name
        mx.log(str(args))
        mx.NativeProject.__init__(self, suite, name, subDir, [], deps, workingSets, results, output, suite.dir, **args)

    def getBuildTask(self, args):
        output_base = self.get_output_base()
        return GraalWasmSourceTask(self, args, output_base)

class GraalWasmSourceTask(mx.NativeBuildTask):
    def __init__(self, project, args, output_base):
        self.output_base = output_base
        self.project = project
        mx.NativeBuildTask.__init__(self, args, project)

    def __str__(self):
        return 'Building {} with Emscripten'.format(self.subject.name)

    def build(self):
        source_dir = os.path.join(self.project.dir, "src", self.project.name, self.project.subDir)
        output_dir = os.path.join(self.output_base, self.project.name)
        mkdir_p(output_dir)
        emcc_dir = mx.get_env("EMCC_DIR", None)
        if not emcc_dir:
            mx.warn("No EMCC_DIR specified - the source programs will not be compiled to .wat and .wasm.")
            return
        mx.log("Building files from the source dir: " + source_dir)
        emcc_cmd = os.path.join(emcc_dir, "emcc")
        flags = ["-Os"]
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                path = os.path.join(root, filename)
                output_path = os.path.join(output_dir, self._remove_extension(filename) + ".js")
                mx.run([emcc_cmd] + flags + [path, "-o", output_path])

    def _remove_extension(self, filename):
        if filename.endswith(".c"):
            return filename[:-2]
        else:
            mx.abort("Unknown extension: " + filename)

    def needsBuild(self, newestInput):
        return (True, None)

    def clean(self, forBuild=False):
        pass
