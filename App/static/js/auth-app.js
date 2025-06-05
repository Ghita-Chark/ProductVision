const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");


function showSignupForm() {
  container.classList.add("sign-up-mode");
}

function showSigninForm() {
  container.classList.remove("sign-up-mode");
}


if (sign_up_btn) {
  sign_up_btn.addEventListener("click", () => {
 
    showSignupForm();
    
    history.pushState({}, '', '/register');
  });
}

if (sign_in_btn) {
  sign_in_btn.addEventListener("click", () => {

    showSigninForm();
    
    history.pushState({}, '', '/login');
  });
}