from viandaware.pedidos.models import Pedido
from viandaware.pedidos.models import User
from viandaware.pedidos.models import Vianda
from viandaware.pedidos.models import CCorriente
from django.contrib import admin
from django.contrib import databrowse

databrowse.site.register(Vianda)
databrowse.site.register(CCorriente)
admin.site.register(Pedido)
admin.site.register(User)
admin.site.register(Vianda)
admin.site.register(CCorriente)
