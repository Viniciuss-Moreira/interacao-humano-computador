import whisper

_loaded_models = {}

def _get_model(model_name):
    if model_name not in _loaded_models:
        _loaded_models[model_name] = whisper.load_model(model_name)
    return _loaded_models[model_name]

def whisper_transcribe(filepath, model_name="base", language="pt"):
    model = _get_model(model_name)
    result = model.transcribe(filepath, language=language)
    return result["text"]

transcrever = whisper_transcribe
