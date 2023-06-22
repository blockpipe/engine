from blockpipe_engine.app.singlefile import SingleFileApplication

code = open('./example_program.py', 'r').read()
app = SingleFileApplication(code)

print(app.get_filters())
