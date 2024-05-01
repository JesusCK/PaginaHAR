var app = document.getElementById('typewriter');



var typewriter = new Typewriter(app, {
  loop: true,
  delay: 75,
});

typewriter
  .typeString('Bienvenido a SeniorSafe')
  .pauseFor(300)
  .start();

  var resultados = []; // Variable para almacenar todos los resultados de la consulta
  var paginaActual = 0; // Variable para almacenar la página actual de resultados
  var resultadosPorPagina = 10; // Número de resultados a mostrar por página

  // Función para mostrar los resultados de la página actual
  function mostrarResultados() {
      var tabla = '';
      var inicio = paginaActual * resultadosPorPagina;
      var fin = inicio + resultadosPorPagina;
      var resultadosPagina = resultados.slice(inicio, fin);
      for (var i = 0; i < resultadosPagina.length; i++) {
          var fecha = new Date(resultadosPagina[i][0]);
          fecha.setHours(fecha.getHours() + 5); // Sumar 5 horas a la fecha
          var formattedDate = fecha.getDate() + '-' + (fecha.getMonth() + 1) + '-' + fecha.getFullYear() + ' ' + fecha.getHours() + ':' + fecha.getMinutes() + ':' + fecha.getSeconds();
          tabla += '<tr><td>' + formattedDate + '</td><td>' + resultadosPagina[i][1] + '</td></tr>';
      }
      document.querySelector('#resultados tbody').innerHTML = tabla;
      document.querySelector('#indice').textContent = 'Página ' + (paginaActual + 1) + ' de ' + Math.ceil(resultados.length / resultadosPorPagina);
  }

  // Función para actualizar la tabla con los resultados de la consulta
  function actualizarTabla(resultados) {
      paginaActual = 0; // Reiniciar la página actual al actualizar los resultados
      mostrarResultados();
  }

  // Función para avanzar a la siguiente página de resultados
  function siguientePagina() {
      if ((paginaActual + 1) * resultadosPorPagina < resultados.length) {
          paginaActual++;
          mostrarResultados();
      }
  }

  // Función para retroceder a la página anterior de resultados
  function anteriorPagina() {
      if (paginaActual > 0) {
          paginaActual--;
          mostrarResultados();
      }
  }
  function generarGraficaCircular(resultados) {
      var acciones = {}; // Objeto para almacenar la frecuencia de cada acción
      for (var i = 0; i < resultados.length; i++) {
      var accion = resultados[i][1];
      if (acciones[accion]) {
      acciones[accion]++;
      } else {
      acciones[accion] = 1;
      }
      }
      var data = [];
      var labels = [];
      for (var accion in acciones) {
      data.push(acciones[accion]);
      labels.push(accion);
      }
      var total = data.reduce((a, b) => a + b, 0);
      var porcentajes = data.map(d => ((d / total) * 100).toFixed(2) + '%');
      var ctx = document.getElementById('graficaCircular').getContext('2d');
      var chart = new Chart(ctx, {
      type: 'pie',
      data: {
      labels: labels,
      datasets: [{
      data: data,
      backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)'
      ],
      borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
      ],
      borderWidth: 1
      }]
      },
      options: {
      responsive: true,
      maintainAspectRatio: false,
      tooltips: {
      callbacks: {
          label: function (tooltipItem, data) {
          var dataset = data.datasets[tooltipItem.datasetIndex];
          var total = dataset.data.reduce((a, b) => a + b, 0);
          var currentValue = dataset.data[tooltipItem.index];
          var percentage = ((currentValue / total) * 100).toFixed(2) + "%";
          return data.labels[tooltipItem.index] + ": " + currentValue + " (" + percentage + ")";
          }
      }
      },
      animation: {
          animateRotate: true,
          animateScale: true
      }
      }
      });
  }
  // Escuchar el evento click del botón "Siguiente"
  document.querySelector('#siguienteBtn').addEventListener('click', function() {
      siguientePagina();
  });

  // Escuchar el evento click del botón "Anterior"
  document.querySelector('#anteriorBtn').addEventListener('click', function() {
      anteriorPagina();
  });

  // Escuchar el evento submit del formulario
  document.querySelector('form').addEventListener('submit', function(e) {
      e.preventDefault(); // Evitar que se recargue la página
      var formData = new FormData(this);
      fetch('/consultar_historicos', {
      method: 'POST',
      body: formData
      })
      .then(response => response.json())
      .then(data => {
      if (data.resultados) {
          resultados = data.resultados; // Almacenar los resultados de la consulta
          actualizarTabla(resultados);
          generarGraficaCircular(resultados);
      } else {
          document.querySelector('#resultados tbody').innerHTML = '<tr><td colspan="2">No se encontraron resultados.</td></tr>';
      }
      })
      .catch(error => {
      console.error('Error:', error);
      });
  });


