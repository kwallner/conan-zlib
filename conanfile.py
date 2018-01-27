from conans import ConanFile, tools, CMake
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
    url = "http://github.com/kwallner/conan-zlib"
    license = "http://www.zlib.net/zlib_license.html"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library " \
                  "(Also Free, Not to Mention Unencumbered by Patents)"

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        z_name = "zlib-%s.tar.gz" % self.version
        tools.download("http://downloads.sourceforge.net/project/libpng/zlib/%s/%s" % (self.version, z_name), z_name, verify=False)
        tools.unzip(z_name)
        os.unlink(z_name)
        files.rmdir("%s/contrib" % self.ZIP_FOLDER_NAME)
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self.ZIP_FOLDER_NAME)
          
        # Conanize
        tools.replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'project(zlib C)', '''
project(zlib C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()
''')
         
        # Fix to build either shared or static
        tools.replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'add_library(zlib SHARED ${ZLIB_SRCS} ${ZLIB_ASMS} ${ZLIB_DLL_SRCS} ${ZLIB_PUBLIC_HDRS} ${ZLIB_PRIVATE_HDRS})', '''
if (BUILD_SHARED_LIBS)
add_library(zlib SHARED ${ZLIB_SRCS} ${ZLIB_ASMS} ${ZLIB_DLL_SRCS} ${ZLIB_PUBLIC_HDRS} ${ZLIB_PRIVATE_HDRS})
endif()                            
''')
        tools.replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'set_target_properties(zlib PROPERTIES DEFINE_SYMBOL ZLIB_DLL)', '''
if (BUILD_SHARED_LIBS)
set_target_properties(zlib PROPERTIES DEFINE_SYMBOL ZLIB_DLL)
endif()                            
''')
        tools.replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'add_library(zlibstatic STATIC ${ZLIB_SRCS} ${ZLIB_ASMS} ${ZLIB_PUBLIC_HDRS} ${ZLIB_PRIVATE_HDRS})', '''
if (NOT BUILD_SHARED_LIBS)
add_library(zlib STATIC ${ZLIB_SRCS} ${ZLIB_ASMS} ${ZLIB_PUBLIC_HDRS} ${ZLIB_PRIVATE_HDRS})
endif()                            
''')
        tools.replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'zlib zlibstatic', 'zlib')
                              
    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON" if self.options.shared or self.options.fPIC else "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.configure(source_dir="%s/%s" % (self.source_folder, self.ZIP_FOLDER_NAME))
        cmake.build()
        cmake.install()
        
    def package(self):
        # Extract the License/s from the header to a file
        with tools.chdir(os.path.join(self.build_folder, self.ZIP_FOLDER_NAME)):
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
            
        self.env_info.ZLIB_ROOT = self.package_folder
