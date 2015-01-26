#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:syntax=on:tabstop=4:nowrap
# author: wincus@gmail.com

import sys, os
from django.core.mail import send_mail
import datetime, locale
from django.conf import settings as conf

def main():
		pathname = os.path.dirname(sys.argv[0])
		sys.path.append(os.path.abspath(pathname))
		sys.path.append(os.path.normpath(os.path.join(os.path.abspath(pathname), '../')))
		os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
		from viandaware.pedidos.models import Pedido,Vianda,User, CCorriente

		locale.setlocale(locale.LC_ALL, '') # para los nombres de dia

		feriados = [ # fuente: http://www.mininterior.gov.ar/servicio/feriados2009.asp
			'2014-01-01', #año nuevo
			'2014-01-31', #?????????
			'2014-02-11', #carnaval
			'2014-02-12', #carnaval
			'2014-02-27', #Dia del bicentenario de la creacion de la bandera
			'2014-03-24', #dia de la memoria
			'2014-04-17', #pascua
			'2014-04-18', #pascua
			'2014-05-01', #Dia del trabajador
			'2014-05-02', #Dia del trabajador
			'2014-05-25', #Primer gobierno patrio
			'2014-06-20', #Dia de la bandera
			'2014-06-21', #Feriado Puente
			'2014-07-09', #Dia de la independencia
			'2014-07-25', #??
			'2014-08-18', #San Martin
			'2014-10-14', #??
			'2014-12-31', #??
			'2014-01-01', #??
			]

		try:
			command = sys.argv.pop(1) 
		except IndexError:
			print "Debe especificarse un argumento"
			sys.exit(9)
		
		today = datetime.date.today()
		
		if today.weekday() == 5 or today.weekday() == 6 or today.isoformat() in feriados:
			#No se envían pedidos los dias no laborales o feriados
			sys.exit(10)

		orderday = today + datetime.timedelta(1) # pedido para mañana
		
		while orderday.weekday() == 5 or orderday.weekday() == 6 or orderday.isoformat() in feriados:
			pass # mañana es feriado o no laboral
			orderday = orderday + datetime.timedelta(1) 

		orderdaytxt =  unicode(orderday.strftime("%A"), "utf8")


		if command == "late-import":
			dia = datetime.date.today()
			while dia.isoweekday() != 1:
				dia = dia - datetime.timedelta(1)

			i = 0
			for line in sys.stdin.readlines():
				line = line.strip()
				if len(line):
					fecha = dia + datetime.timedelta(i/5)
					v = Vianda(nombre=line,datetime=fecha)
					v.save()
					print "%s para el %s" % (line,str(fecha))
					i+=1
			sys.exit(0)


		if command == "import":
			dia = datetime.date.today()
			while dia.isoweekday() != 1:
				dia = dia + datetime.timedelta(1)

			i = 0
			for line in sys.stdin.readlines():
				line = line.strip()
				if len(line):
					fecha = dia + datetime.timedelta(i/5)
					v = Vianda(nombre=line,datetime=fecha)
					v.save()
					print "%s para el %s" % (line,str(fecha))
					i+=1
			sys.exit(0)
				
		elif command == "notify":
			v = Vianda()
			v.Viandas4DayN(orderday) or sys.exit(3)
			users = User.objects.all()
			
			for user in users:
					if user.notify and not user.myOrders4DayN(orderday):
							cuerpo = u""
							cuerpo = u"%s:\nNo tengo registrado tu pedido para el %s.\n\nLas opciones son:\n\n%s" % (user.nombre, orderdaytxt, v.Viandas4DayNinText(orderday))
							cuerpo += u"\n\nTu saldo al dia de hoy es de $" + str(user.saldo)
							
							if user.saldo < 0:
								cuerpo += u"  ¡¡¡¡¡¡  Recordá depositar plata en la caja común !!!!!!"
							
							cuerpo += u"\nEl pedido se envía a las 13:30hs. Los pedidos hechos con posterioridad se omitirán.\n"
							cuerpo += u"\n\nPodes hacer tu pedido aca: %s" % "http://viandaware.com.ar/pedido/" + user.nombre + "/"
							cuerpo += u"\n\nPowered by Viandaware"
							send_mail('Recordatorio'  , cuerpo , conf.NOT_REMITENTE, [user.email])
							print "Mail enviado a %s\n" % user.nombre 
			
			sys.exit(0)

		elif command == "order":
			# recuperar los pedidos para mañana
			# enviar los mails
			p = Pedido()
			cc = CCorriente()
			destinos = [conf.MAIL_YANINA] + conf.ALWAYS_CC
		
			p.Orders4DayN(orderday) or sys.exit(2)

			asunto = "Pedido para el %s " % orderdaytxt
			cuerpo = "Hola! Pedido para el %s:\n\n" % orderdaytxt
				
			for pedido in p.Orders4DayN(orderday):
						if not pedido.user.email in destinos:
								destinos.append(pedido.user.email)	
						cuerpo += unicode(pedido) + "\n\n"  
						pedido.user.descontar(conf.COSTO_VIANDA * pedido.cant) 
						pedido.user.save()	
						cc = CCorriente(user_id=pedido.user_id, saldo=conf.COSTO_VIANDA * pedido.cant * -1, datetime=orderday, label=str(pedido))
						cc.save()

			cuerpo += "\n\nMuchas Gracias!"
			send_mail(asunto, cuerpo, 'order@viandaware.com.ar', destinos)
			sys.exit(0)
		
		else:
			print "Comando %s desconocido" % command
					
		sys.exit(0)

if __name__ == '__main__':
    main()
