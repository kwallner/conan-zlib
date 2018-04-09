from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
from conans.util import files
from conans import __version__ as conan_version
import os

class ZlibConan(ConanFile):
    name = "zlib"
    version = "1.2.11"
    ZIP_FOLDER_NAME = "zlib-%s" % version
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    exports_sources = ["CMakeLists.txt", "patches/zlib-1.2.11_shared_xor_static.patch"]
    url = "http://github.com/kwallner/conan-zlib"
    license = "http://www.zlib.net/zlib_license.html"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library " \
                  "(Also Free, Not to Mention Unencumbered by Patents)"
    no_copy_source = True

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        z_name = "zlib-%s.tar.gz" % self.version
        tools.download("http://downloads.sourceforge.net/project/libpng/zlib/%s/%s" % (self.version, z_name), z_name, verify=False)
        tools.unzip(z_name)
        os.unlink(z_name)
        tools.patch(patch_file="patches/zlib-1.2.11_shared_xor_static.patch")
        files.rmdir("%s/contrib" % self.ZIP_FOLDER_NAME)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ZLIB_SHARED"] = self.options.shared
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.shared or self.options.fPIC
        cmake.configure(source_dir="%s/%s" % (self.source_folder, self.ZIP_FOLDER_NAME))
        cmake.build()
        cmake.install()

    def package(self):
        # Extract the License/s from the header to a file
        with tools.chdir(os.path.join(self.source_folder, self.ZIP_FOLDER_NAME)):
            tmp = tools.load("zlib.h")
            license_contents = tmp[2:tmp.find("*/", 1)]
            tools.save("LICENSE", license_contents)

        # Copy the license files
        self.copy("LICENSE", src=self.ZIP_FOLDER_NAME, dst=".")

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['zlib']
            if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
                self.cpp_info.libs[0] += "d"
        else:
            self.cpp_info.libs = ['z']
