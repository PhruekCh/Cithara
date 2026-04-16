from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from domain.models import Song, Library, GenerationJob
from domain.generation import get_generator
from domain.serializers import (
    GenerationRequestSerializer,
    GenerationJobSerializer,
)


class GenerateSongView(APIView):
    """
    POST /api/generate/

    Accepts generation parameters, delegates to the active strategy,
    creates Song + GenerationJob records, and returns the result.
    """

    def post(self, request):
        serializer = GenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Verify the library exists
        try:
            library = Library.objects.get(pk=data['library'])
        except Library.DoesNotExist:
            return Response(
                {"error": f"Library {data['library']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create Song record
        song = Song.objects.create(
            library=library,
            title=data['title'],
            duration=0,  # will be updated once generation completes
            genre=data['genre'],
            mood=data['mood'],
            occasion=data['occasion'],
        )

        # Delegate to the active strategy
        generator = get_generator()
        gen_request = {
            "prompt": data['prompt'],
            "style": data['style'],
            "title": data['title'],
        }

        try:
            result = generator.generate(gen_request)
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Determine strategy name
        strategy_name = (
            GenerationJob.Strategy.MOCK
            if type(generator).__name__ == 'MockSongGeneratorStrategy'
            else GenerationJob.Strategy.SUNO
        )

        # Create GenerationJob record
        job = GenerationJob.objects.create(
            song=song,
            task_id=result['task_id'],
            status=result.get('status', 'PENDING'),
            strategy_used=strategy_name,
        )

        # If the strategy already returned SUCCESS (mock), update Song
        if result.get('status') == 'SUCCESS' and result.get('data'):
            suno_data = result['data'].get('sunoData', [])
            if suno_data:
                first = suno_data[0]
                job.audio_url = first.get('audioUrl')
                job.stream_audio_url = first.get('streamAudioUrl')
                job.image_url = first.get('imageUrl')
                job.save()

                song.audio_url = first.get('audioUrl')
                song.duration = int(first.get('duration', 0))
                song.save()

        return Response(
            GenerationJobSerializer(job).data,
            status=status.HTTP_201_CREATED,
        )


class GenerationStatusView(APIView):
    """
    GET /api/generate/<task_id>/status/

    Polls the active strategy for the current status of a generation task
    and updates the local GenerationJob record.
    """

    def get(self, request, task_id):
        try:
            job = GenerationJob.objects.get(task_id=task_id)
        except GenerationJob.DoesNotExist:
            return Response(
                {"error": f"Task {task_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # If already completed, just return stored data
        if job.status == 'SUCCESS':
            return Response(GenerationJobSerializer(job).data)

        # Poll the strategy
        generator = get_generator()

        try:
            result = generator.check_status(task_id)
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Update job record
        job.status = result.get('status', job.status)
        if result.get('error_message'):
            job.error_message = result['error_message']
            job.status = 'FAILED'

        if result.get('status') == 'SUCCESS' and result.get('data'):
            suno_data = result['data'].get('sunoData', [])
            if suno_data:
                first = suno_data[0]
                job.audio_url = first.get('audioUrl')
                job.stream_audio_url = first.get('streamAudioUrl')
                job.image_url = first.get('imageUrl')

                # Update the parent Song too
                job.song.audio_url = first.get('audioUrl')
                job.song.duration = int(first.get('duration', 0))
                job.song.save()

        job.save()

        return Response(GenerationJobSerializer(job).data)
