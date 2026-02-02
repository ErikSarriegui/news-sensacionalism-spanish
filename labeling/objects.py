from pydantic import BaseModel, Field, ConfigDict

class ClickbaitAnalysis(BaseModel):
    # ---------------------------------------------------------
    model_config = ConfigDict(extra='forbid')
    # ---------------------------------------------------------
    clickbait_reasoning: str = Field(
        ..., 
        description="Explicación concisa (máx 20 palabras) citando el rasgo lingüístico detectado (ej. 'Usa brecha de curiosidad', 'Adjetivos exagerados')."
    )

    is_clickbait: bool = Field(
        ..., 
        description="True si el titular es clickbait (sensacionalista/engañoso), False si es informativo."
    )

class SensationalismAnalysis(BaseModel):
    # ---------------------------------------------------------
    model_config = ConfigDict(extra='forbid')
    # ---------------------------------------------------------
    sensationalist_reasoning: str = Field(
        ..., 
        description="Explicación concisa (máx 30 palabras) identificando qué elemento detonó la clasificación (ej. 'Discrepancia grave entre título y hechos', 'Uso excesivo de adjetivos alarmistas', 'Tono neutro y factual')."
    )

    is_sensationalist: bool = Field(
        ..., 
        description="True si el artículo es sensacionalista (manipula emociones/exagera), False si es periodismo neutral/riguroso."
    )