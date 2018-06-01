{
  "conditions": [
    ["OS==\"win\"", {
      "variables": {
        "VCPKG_Path%": "C:/libs/installed/x64-windows-static"
      },
      # "defines": ["USING_SHARED_PODOFO=1"]
    }],
  ],
  "targets": [
    # {
    #   "target_name": "npdf-postbuild",
    #   "dependencies": ["npdf"],
    #   "conditions": [
    #     ["OS==\"win\"", {
    #       "copies": [{
    #         "destination": "<(PRODUCT_DIR)",
    #         "files": [
    #           "<(VCPKG_Path)/bin/zlib1.dll",
    #           "<(VCPKG_Path)/bin/libpng16.dll",
    #           "<(VCPKG_Path)/bin/fontconfig.dll",
    #           "<(VCPKG_Path)/bin/jpeg62.dll",
    #           "<(VCPKG_Path)/bin/expat.dll",
    #           "<(VCPKG_Path)/bin/freetype.dll",
    #           "<(VCPKG_Path)/bin/libbz2.dll",
    #           "<(VCPKG_Path)/bin/libcharset.dll",
    #           "<(VCPKG_Path)/bin/libeay32.dll",
    #           "<(VCPKG_Path)/bin/libiconv.dll",
    #           "<(VCPKG_Path)/bin/ssleay32.dll",
    #           "<(VCPKG_Path)/bin/tiff.dll",
    #           "<(VCPKG_Path)/bin/tiffxx.dll",
    #           "<(VCPKG_Path)/bin/turbojpeg.dll"
    #         ]
    #       }]
    #     }]
    #   ]
    # },
    {
      "target_name": "npdf",
      'include_dirs': ["<!@(node -p \"require('node-addon-api').include\")"],
      'dependencies': ["<!(node -p \"require('node-addon-api').gyp\")"],
      'cflags_cc': ['-std=c++14'],
      'cflags_cc!': [ '-fno-exceptions', '-fno-rtti' ],
      'cflags!': [ '-fno-exceptions', '-fno-rtti' ],
      'xcode_settings': {
        'GCC_ENABLE_CPP_EXCEPTIONS': 'YES',
        'CLANG_CXX_LIBRARY': 'libc++',
        'MACOSX_DEPLOYMENT_TARGET': '10.7',
      },
      'msvs_settings': {
        'VCCLCompilerTool': {
          'ExceptionHandling': 1,
        },
      },
      "dependencies": [
        "deps/podofo.gypi:libpodofo"
      ],
      "sources": [
        "src/addon.cc",
        "src/ErrorHandler.cc",
    		"src/doc/Action.cc",
        "src/doc/Annotation.cc",
    		"src/doc/BaseDocument.cc",
    		"src/doc/Button.cc",
        "src/doc/CheckBox.cc",
        "src/doc/Document.cc",
    		"src/doc/Destination.cc",
        "src/doc/Encoding.cc",
        "src/doc/Encrypt.cc",
        "src/doc/ExtGState.cc",
        "src/doc/Field.cc",
        "src/doc/FileSpec.cc",
        "src/doc/Font.cc",
        "src/doc/Form.cc",
        "src/doc/Image.cc",
        "src/doc/ListField.cc",
    		"src/doc/Outline.cc",
        "src/doc/Page.cc",
        "src/doc/Painter.cc",
    		"src/doc/PushButton.cc",
        "src/doc/Rect.cc",
        "src/doc/SignatureField.cc",
        "src/doc/Signer.cc",
    		"src/doc/StreamDocument.cc",
        "src/doc/TextField.cc",
        "src/doc/SimpleTable.cc",
        "src/doc/ComboBox.cc",
        "src/doc/ListBox.cc",
        "src/base/Array.cc",
        "src/base/Dictionary.cc",
        "src/base/Obj.cc",
        "src/base/Stream.cc",
        "src/crypto/Signature.cc",
        "src/base/Data.cc",
        "src/base/ContentsTokenizer.cc"
      ],
      # !!!! Windows NPDF Build !!!! #
      "conditions": [
        ["OS==\"win\"", {
          "link_settings": {
            "libraries": ["ws2_32"]
          },
          # "libraries": [
          #   "-l<(VCPKG_Path)/lib/bz2.lib",
          #   "-l<(VCPKG_Path)/lib/expat.lib",
          #   "-l<(VCPKG_Path)/lib/fontconfig.lib",
          #   "-l<(VCPKG_Path)/lib/freetype.lib",
          #   "-l<(VCPKG_Path)/lib/jpeg.lib",
          #   "-l<(VCPKG_Path)/lib/libcharset.lib",
          #   "-l<(VCPKG_Path)/lib/libeay32.lib",
          #   "-l<(VCPKG_Path)/lib/libiconv.lib",
          #   "-l<(VCPKG_Path)/lib/libpng16.lib",
          #   "-l<(VCPKG_Path)/lib/lzma.lib",
          #   "-l<(VCPKG_Path)/lib/ssleay32.lib",
          #   "-l<(VCPKG_Path)/lib/tiff.lib",
          #   "-l<(VCPKG_Path)/lib/tiffxx.lib",
          #   "-l<(VCPKG_Path)/lib/turbojpeg.lib",
            # "-l<(VCPKG_Path)/lib/zlib.lib",
          # ],
          # "include_dirs": [
          #   "<(VCPKG_Path)/include",
          #   "<(VCPKG_Path)/fontconfig", 
          #   "<(VCPKG_Path)/freetype", 
          #   "<(VCPKG_Path)/libpng16", 
          #   "<(VCPKG_Path)/lzma", 
          #   "<(VCPKG_Path)/openssl", 
          # ],
          "configurations": {
            "Debug": {
              "msvs_settings": {
                "VCCLCompilerTool": {
                  "WarningLevel": 4,
                  "ExceptionHandling": 1,
                  "DisableSpecificWarnings": [
                    4100, 4127, 4201, 4244, 4267, 4506, 4611, 4714, 4512
                  ]
                }
              }
            },
            "Release": {
              "msvs_settings": {
                "VCCLCompilerTool": {
                  "WarningLevel": 4,
                  "ExceptionHandling": 1,
                  "DisableSpecificWarnings": [
                    4100, 4127, 4201, 4244, 4267, 4506, 4611, 4714, 4512
                  ]
                }
              }
            }
          }
        }, 

      # !!!! Linux NPDF Build !!!! #
        {  # "OS!=\"win\""
          'conditions': [
            ['node_shared_openssl=="false"', {
              'include_dirs': [
                '<(node_root_dir)/deps/openssl/openssl/include'
              ],
              'conditions': [
                 ["target_arch=='ia32'", {
                   "include_dirs": [ "<(node_root_dir)/deps/openssl/config/piii" ]
                }],
                ["target_arch=='x64'", {
                  "include_dirs": [ "<(node_root_dir)/deps/openssl/config/k8" ]
                }],
                ["target_arch=='arm'", {
                  "include_dirs": [ "<(node_root_dir)/deps/openssl/config/arm" ]
                }]
              ]
            }]
          ],
          "libraries": [
            '<!@(pkg-config openssl --libs)',
            '<!@(pkg-config fontconfig --libs)',
            '<!@(pkg-config libpng --libs)',
            '<!@(pkg-config libjpeg --libs)',
            '<!@(pkg-config libpng --libs)',
            '<!@(pkg-config freetype2 --libs)',
            '<!@(pkg-config libidn --libs)',
            '<!@(pkg-config libtiff-4 --libs)',
          ],
          "include_dirs": [
            '<!@(pkg-config openssl --cflags-only-I | sed s/-I//g)',
            '<!@(pkg-config libpng --cflags-only-I | sed s/-I//g)',
            '<!@(pkg-config fontconfig --cflags-only-I | sed s/-I//g)',
            '<!@(pkg-config freetype2 --cflags-only-I | sed s/-I//g)',
            '<!@(pkg-config libjpeg --cflags-only-I | sed s/-I//g)',
            '<!@(pkg-config libidn --cflags-only-I | sed s/-I//g)',
            '<!@(pkg-config libtiff-4 --cflags-only-I | sed s/-I//g)',
          ]
        }],
      ]
    }
  ],
  'target_defaults': {
    'configurations': {
      'Debug': {
        'conditions': [
          ['OS == "linux" or OS == "freebsd" or OS == "openbsd"', {
            'cflags_cc': ['-g']
          }]
        ]
      },
      'Release': {
        'conditions': [
          ['OS == "linux" or OS == "freebsd" or OS == "openbsd"', {
            'cflags_cc': ['-O3']
          }]
        ]
      }
    }
  }
}
