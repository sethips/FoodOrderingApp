from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from users.permission import IsClient
from rest_framework.response import Response
from users.serializers.restaurantadmin.restaurantadmin_restaurant_serializers import RestaurantSerializer,\
    MenuSerializer, SubMenuSerializer, ItemSerializer, OrderSerilizer
from restaurants.constants import WAITING
from restaurants.models import Restaurant, Menu, SubMenu, Item, Order


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def client_list_restaurants(request):
    if request.method == "POST":
        restaurants = Restaurant.objects.all().order_by("name")[request.data["start"]:request.data["end"]]
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def client_list_restaurant(request, restaurant_id):
    if request.method == "GET":
        restaurant = Restaurant.objects.filter(id=restaurant_id)
        if len(restaurant) == 0:
            return Response("No restaurant with this id.", status=status.HTTP_400_BAD_REQUEST)
        serializer = RestaurantSerializer(restaurant[0])
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def client_list_restaurant_menus(request, restaurant_id):
    if request.method == "GET":
        restaurant = Restaurant.objects.filter(id=restaurant_id)
        if len(restaurant) == 0:
            return Response("No restaurant with this id.", status=status.HTTP_400_BAD_REQUEST)
        menu = Menu.objects.filter(restaurant_id=restaurant_id)
        serializer = MenuSerializer(menu, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def client_list_restaurant_menu(request, menu):
    if request.method == "GET":
        menu_id = menu
        menu = Menu.objects.filter(id=menu_id)
        if len(menu) == 0:
            return Response("No menu with this id.", status=status.HTTP_400_BAD_REQUEST)
        submenu = SubMenu.objects.filter(menu_id=menu_id)
        serializer = SubMenuSerializer(submenu, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def client_list_restaurant_submenu(request, submenu):
    if request.method == "GET":
        submenu_id = submenu
        submenu = SubMenu.objects.filter(id=submenu_id)
        if len(submenu) == 0:
            return Response("No submenu with this id.", status=status.HTTP_400_BAD_REQUEST)
        items = Item.objects.filter(submenu_id=submenu_id)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsClient])
def client_order(request):
    if request.method == "POST":
        items = request.data["items"]["IDs"]
        total_price = 0
        cart = []
        for i in items:
            item = Item.objects.filter(id=i)
            if len(item) == 0:
                return Response("No Item with this id.", status=status.HTTP_400_BAD_REQUEST)
            cart.append(item[0])
            total_price += item[0].price
        if len(cart) == 0:
            return Response("Empty cart.", status=status.HTTP_400_BAD_REQUEST)
        total_price *= 1.35
        order = Order.objects.create(client=request.user.user_client, status=WAITING, price=total_price)
        order.items.set(cart)
        order.save()
        serializer = OrderSerilizer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
