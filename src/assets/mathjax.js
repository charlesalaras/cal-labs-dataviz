/* window.MathJax = {
   tex: {
      inlineMath: [['$','$']]
   }
};
*/
/*
(function() {
   var script = document.createElement('script');
   script.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6';
   script.async = true;
   document.head.appendChild(script);
})
(function() {
   var script = document.createElement('script');
   script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
   script.async = true;
   document.head.appendChild(script);
})
*/
setInterval("MathJax.Hub.Queue(['Typeset', MathJax.Hub])", 1000);
console.log("mathjax.js loaded!")
