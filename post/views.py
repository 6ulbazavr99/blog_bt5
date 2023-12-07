from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from comment.serializers import CommentSerializer
from like.models import Favorite
from like.serializers import LikeUserSerializer
from post import serializers
from post.models import Post
from post.permissions import IsOwner, IsOwnerOrAdmin


class StandardResultPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandardResultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title', 'body')
    filterset_fields = ('owner', 'category')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return serializers.PostCreateUpdateSerializer
        return serializers.PostDetailSerializer

    # api/v1/posts/ GET -> list
    # api/v1/posts/ POST -> create
    # api/v1/posts/id/ PATCH/PUT -> update
    # api/v1/posts/id/ GET -> detail
    # api/v1/posts/id/ DELETE -> destroy

    def get_permissions(self):
        # удалять может только автор поста или админы
        if self.action == 'destroy':
            return [IsOwnerOrAdmin(), ]
        # обновлять может только автор поста
        elif self.action in ('update', 'partial_update'):
            return [IsOwner(), ]
        # просматривать могут все (List, retrieve)
        # но создавать может залогиненный пользователь
        return [permissions.IsAuthenticatedOrReadOnly(), ]

    # api/v1/posts/ GET -> list
    # api/v1/posts/ POST -> create
    # api/v1/posts/id/ PATCH/PUT -> update
    # api/v1/posts/id/ GET -> detail
    # api/v1/posts/id/ DELETE -> destroy
    # api/v1/posts/id/comments/ GET -> comments

    @action(['GET'], detail=True)
    def comments(self, request, pk):
        # post = Post.objects.get(id=pk)
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(instance=comments, many=True)
        return Response(serializer.data, status=200)

    # .../api/v1/posts/id/likes/
    @action(['GET'], detail=True)
    def likes(self, request, pk):
        post = self.get_object()
        likes = post.likes.all()
        serializer = LikeUserSerializer(instance=likes, many=True)
        return Response(serializer.data, status=200)

    # .../api/v1/posts/id/favorites/
    @action(['POST', 'DELETE'], detail=True)
    def favorites(self, request, pk):
        post = self.get_object()
        user = request.user
        favorite = user.favorites.filter(post=post)

        if request.method == 'POST':
            if favorite.exists():
                return Response({'mgs': 'Already in Favorites'}, status=400)
            Favorite.objects.create(owner=user, post=post)
            return Response({'mgs': 'Added to Favorites'}, status=201)

        if favorite.exists():
            favorite.delete()
            return Response({'msg': 'Deleted from Favorites'}, status=204)
        return Response({'msg': 'Post Not Found in Favorites'}, status=404)



# class PostListCreateView(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return serializers.PostListSerializer
#         return serializers.PostCreateUpdateSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#
# class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.objects.all()
#
#     def get_serializer_class(self):
#         if self.request.method in ('PUT', 'PATCH'):
#             return serializers.PostCreateUpdateSerializer
#         return serializers.PostDetailSerializer
#
#     def get_permissions(self):
#         if self.request.method in ('PUT', 'PATCH'):
#             return [permissions.IsAuthenticated(), IsOwner()]
#         elif self.request.method == 'DELETE':
#             return [IsOwnerOrAdmin()]
#         return [permissions.AllowAny(),]
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#


