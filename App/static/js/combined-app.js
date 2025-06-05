document.addEventListener("DOMContentLoaded", function() {
    const sign_in_btn = document.querySelector("#sign-in-btn");
    const sign_up_btn = document.querySelector("#sign-up-btn");
    const container = document.querySelector(".auth-container");
  
    if (sign_up_btn) {
      sign_up_btn.addEventListener("click", () => {
        container.classList.add("sign-up-mode");
      });
    }
  
    if (sign_in_btn) {
      sign_in_btn.addEventListener("click", () => {
        container.classList.remove("sign-up-mode");
      });
    }

    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages) {
      flashMessages.forEach(message => {
        setTimeout(() => {
          message.style.opacity = '0';
          message.style.transform = 'translateY(-20px)';
          message.style.transition = 'opacity 0.5s, transform 0.5s';
        }, 5000);
      });
    }
  });