var app = document.getElementById('typewriter');



var typewriter = new Typewriter(app, {
  loop: true,
  delay: 75,
});

typewriter
  .typeString('Bienvenido a SeniorSafe')
  .pauseFor(300)
  .start();




