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

  let list = document.querySelectorAll(".navigation li");
  
  function activeLink() {
    list.forEach((item) => {
      item.classList.remove("hovered");
    });
    this.classList.add("hovered");
  }
  
  list.forEach((item) => item.addEventListener("mouseover", activeLink));
  

  let toggle = document.querySelector(".toggle");
  let navigation = document.querySelector(".navigation");
  let main = document.querySelector(".main");
  
  if (toggle) {
    toggle.onclick = function () {
      navigation.classList.toggle("active");
      main.classList.toggle("active");
    };
  }
  
  // Tab functionality
  function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    
    const tabElement = document.getElementById(tabId);
    if (tabElement) {
      tabElement.classList.add('active');
      document.querySelector(`button[onclick="showTab('${tabId}')"]`).classList.add('active');
    }
  }
  
  // File input display
  const fileInput = document.getElementById('csv-file');
  if (fileInput) {
    fileInput.addEventListener('change', function(e) {
      const fileName = document.getElementById('file-name');
      if (fileName) {
        fileName.textContent = this.files[0].name;
      }
    });
  }