from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Entrenador, Clase


class ClaseAPITestCase(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='tester',
			password='12345',
			email='tester@example.com',
		)
		self.entrenador = Entrenador.objects.create(
			nombre='Juan Perez',
			especialidad='Cardio',
			telefono='123456789',
			fecha_contratacion='2024-01-01',
		)
		self.clase = Clase.objects.create(
			nombre='Yoga Matutino',
			descripcion='Clase de yoga para comenzar el día',
			fecha_hora='2024-01-02T08:00:00Z',
			duracion_minutos=60,
			entrenador=self.entrenador,
			max_participantes=20,
		)
		self.clase.participantes.add(self.user)

	def test_listado_clases_api(self):
		url = reverse('clase-list')
		response = self.client.get(url)

		self.assertEqual(response.status_code, 200)
		self.assertGreaterEqual(len(response.data['results']), 1)
		clase_serializada = response.data['results'][0]
		self.assertEqual(clase_serializada['nombre'], 'Yoga Matutino')
		self.assertIn(self.user.id, clase_serializada['participantes'])
