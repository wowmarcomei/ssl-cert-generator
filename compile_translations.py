import os
from babel.messages.frontend import compile_catalog

def compile_translations():
    translations_dir = 'translations'
    for lang in os.listdir(translations_dir):
        lang_dir = os.path.join(translations_dir, lang, 'LC_MESSAGES')
        if os.path.isdir(lang_dir):
            po_file = os.path.join(lang_dir, 'messages.po')
            mo_file = os.path.join(lang_dir, 'messages.mo')
            if os.path.exists(po_file):
                print(f"Compiling translations for {lang}")
                compiler = compile_catalog()
                compiler.input_file = po_file
                compiler.output_file = mo_file
                compiler.finalize_options()
                compiler.run()
                print(f"Compiled {mo_file}")
            else:
                print(f"No .po file found for {lang}")

if __name__ == '__main__':
    compile_translations()