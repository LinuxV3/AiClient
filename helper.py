import sys


def run_translator():
    import plugins.Translator.app as app
    app.run()


def run_image_generator():
    import plugins.ImageGenerator.app as app
    app.run()


def run_settings():
    import plugins.Settings.app as app
    app.run()


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[0] == 't':
        run_translator()
    elif args[0] == 'i':
        run_image_generator()
    elif args[0] == 's':
        run_settings()

