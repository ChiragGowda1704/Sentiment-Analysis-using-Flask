document.addEventListener('DOMContentLoaded', function() {
  // Character counter
  const textInput = document.getElementById('textInput');
  const charCount = document.getElementById('charCount');
  
  textInput.addEventListener('input', function() {
      charCount.textContent = this.value.length;
  });

  // Form submission handler
  const form = document.getElementById('sentimentForm');
  const analyzeBtn = document.getElementById('analyzeBtn');
  
  form.addEventListener('submit', function() {
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = '<span>Analyzing...</span> <i class="fas fa-spinner"></i>';
      analyzeBtn.classList.add('loading');
  });

  // Auto-resize textarea
  function autoResize() {
      textInput.style.height = 'auto';
      textInput.style.height = textInput.scrollHeight + 'px';
  }
  
  textInput.addEventListener('input', autoResize);
  autoResize(); // Initialize
});