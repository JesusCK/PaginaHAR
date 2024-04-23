var app = document.getElementById('typewriter');



var typewriter = new Typewriter(app, {
  loop: true,
  delay: 75,
});

typewriter
  .typeString('Bienvenido a tu sistema mas seguro')
  .pauseFor(300)
  .start();