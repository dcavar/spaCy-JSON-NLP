from spacyjsonnlp import SpacyPipeline
from pyjsonnlp.microservices.flask_server import FlaskMicroservice

app = FlaskMicroservice(__name__, SpacyPipeline(), base_route='/')
app.with_constituents = True
app.with_coreferences = True
app.with_dependencies = True
app.with_expressions = True

if __name__ == "__main__":
    app.run(debug=True, port=5001)
