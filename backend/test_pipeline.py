from transcriber import transcribe_audio
from agent import orchestrer
import json

result = transcribe_audio(r'C:\Users\kouak\Downloads\Explication Ddf.ogg')
print('Durée audio:', result['duree_totale'], 'secondes')

plan = orchestrer(result, 'Seconde', 'Mathematiques')
timeline = plan['timeline']

print('Nombre de segments:', len(timeline))
print('Durée couverte par la timeline:')
for i, seg in enumerate(timeline):
    print(f"  Segment {i+1}: {seg['timestamp_debut']}s -> {seg['timestamp_fin']}s ({seg['type']})")

dernier = timeline[-1]
print('Fin dernier segment:', dernier['timestamp_fin'], 'secondes')
print('Audio non couvert:', result['duree_totale'] - dernier['timestamp_fin'], 'secondes')