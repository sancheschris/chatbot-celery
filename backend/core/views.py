from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from core.models import AiChatSession
from core.serializers import AiChatSessionSerializer

@api_view(['POST'])
def create_chat_session(request):
    """Create a new chat session."""
    session = AiChatSession.objects.create()
    serializer = AiChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
def chat_session(request, session_id):
    """Retrieve a chat session and its messages"""
    session = get_object_or_404(AiChatSession, id=session_id)
    serializer = AiChatSessionSerializer(session)
    
    if request.method == 'POST':
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message content is required.'},
                             status=status.HTTP_400_BAD_REQUEST)
        session.send(message)

    return Response(serializer.data)