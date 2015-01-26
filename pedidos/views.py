from django.http import HttpResponse
from django.template import Context, loader
from viandaware.pedidos.models import Vianda,User,Pedido,CCorriente
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.db import models
import datetime

def addorder(request,user):
		pedidos = []
		changes = False
		total=0

		if not user:
			return HttpResponse("Debe especificar un usuario")
			
		try:
			u = User.objects.get(nombre=user)

		except (models.ObjectDoesNotExist):
			return HttpResponse("El user %s no existe" % user)
			
			
		
		if request.method == 'POST':
			for key,value in request.POST.iteritems():
				p = None
				if key[:4] == "cant":
					vianda_id = key[5:]
					vianda_cant = int(value)
				
					try:
						p = Pedido.objects.get(pedido=vianda_id,user=u.id)

					except (models.ObjectDoesNotExist):
						# no existe
						if vianda_cant:
								p = Pedido(pedido_id=vianda_id,user_id=u.id,cant=vianda_cant)
								p.save()
								changes = True
	
					except (models.AssertionError):
						# esta duplicado
						print u'error, esto no deberia pasar!'

					else:
						# existe
						if vianda_cant:					
								p.cant = vianda_cant
								p.save()
								changes = True
						else:
								p.delete()
								changes = True
				
				if key[:4] == "pago":
					monto = int(value)
					
					if monto:
						print "procedo a acreditar %s a %s" % (str(monto), str(u.nombre))
						u.acreditar(monto)
						u.save()
						cc = CCorriente(user_id=u.id, saldo=monto, datetime=datetime.date.today(), label="Pago")
						cc.save()
						changes = True

		else:
			changes = False

		# para recuperar los pedidos
		V = Vianda()
		viandas = V.startingtomorrow()
		for vianda in viandas:
				p  =  Pedido.objects.filter(user=u.id,pedido=vianda.id)
				
				if p.count():
					# hay pedidos hechos
					pedidos.append(p[0])
				else:
					# no hay pedidos
					pedidos.append(Pedido(pedido_id=vianda.id,user_id=u.id,cant=0))
					
		# para recuperar los saldos
		users = User.objects.all()
		for x in users:
			total+=x.saldo
		
		# para recuperar el historial 
		CC = CCorriente()
		CC.user = u
		ccs = CC.lastmov()

		return render_to_response('mispedidos.html', locals())

