# -*- coding: utf-8 -*- 
# vim:syntax=on:tabstop=4:nowrap

from django.db import models
from django.forms import ModelForm
import datetime

class Vianda(models.Model):
	nombre = models.CharField(max_length=100)
	datetime = models.DateTimeField('Vianda para el dia')

	def startingtomorrow(self):
		today = datetime.date.today()
		return Vianda.objects.filter(datetime__gt=today.isoformat()).order_by("datetime")

	def Viandas4DayN(self,day):
		return Vianda.objects.filter(datetime__contains=day)

	def Viandas4DayNinText(self,day):
		string = ""
		viandas = self.Viandas4DayN(day)
		for vianda in viandas:
			string += "* " + unicode(vianda) + '\n'
		
		return string

	def __unicode__(self):
		return unicode(self.nombre)

	class Admin:
		pass

class User(models.Model):
	nombre = models.CharField(max_length=100)
	email = models.CharField(max_length=50)
	notify = models.BooleanField("Queres recibir notificaciones por mail?")
	saldo = models.IntegerField(default=0)

	def descontar(self, monto):
		self.saldo -= monto
		return self.saldo

	def acreditar(self,monto):
		self.saldo += monto
		return self.saldo

	def color(self):
		if self.saldo == 0:
			return "lightgrey"
		elif self.saldo > 0:
			return "lightgreen"
		else:
			return "red"
			
	def myOrders(self):
		return  Pedido.objects.filter(user__nombre=self.nombre,pedido__datetime__gte=datetime.date.today())

	def myOrders4DayN(self,orderday):
		return Pedido.objects.filter(user__nombre=self.nombre,pedido__datetime__contains=orderday)

	def __unicode__(self):
		return self.nombre

	class Admin:
		pass

class Pedido(models.Model):
	pedido = models.ForeignKey(Vianda)
	user = models.ForeignKey(User)
	cant = models.IntegerField("cantidad")

	class Admin:
		pass

	def Orders4DayN(self,day):
		return Pedido.objects.filter(pedido__datetime__contains=day)

	def __unicode__(self):
		return "%s para %s (x %s) [%s]" % (unicode(self.pedido), unicode(self.user),unicode(self.cant), unicode(self.pedido.datetime))

class CCorriente(models.Model):
	user = models.ForeignKey(User)
	saldo = models.IntegerField()
	datetime = models.DateTimeField('Saldo al')
	label = models.CharField(max_length=100)

	def lastmov(self):
		return CCorriente.objects.filter(user=self.user).reverse().order_by("datetime")[:30]
	
	def __unicode__(self):
		return " %s  %s  %s  %s  "  % (unicode(self.user.nombre),unicode(self.label),unicode(self.datetime),unicode(self.saldo))

	def color(self):
		if self.saldo == 0:
			return "lightgrey"
		elif self.saldo > 0:
			return "lightgreen"
		else:
			return "lightyellow"

	class Admin:
		pass
