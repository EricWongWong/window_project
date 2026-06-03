document.addEventListener('DOMContentLoaded', function () {
    const burger = document.getElementById('burgerBtn');
    const menu = document.getElementById('main-menu');
    
    if (burger) {
        burger.addEventListener('click', function() {
            menu.classList.toggle('active');
        });
    }

    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        link.addEventListener('click', function() {
            if (menu) menu.classList.remove('active');
        });
    });

    const bookingForm = document.querySelector('form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function (e) {
            const name = document.querySelector('input[name="name"]')?.value.trim();
            const phone = document.querySelector('input[name="phone"]')?.value.trim();
            const address = document.querySelector('input[name="address"]')?.value.trim();
            const date = document.querySelector('input[name="booking_date"]')?.value;

            if (!name || !phone || !address || !date) {
                alert('請填寫所有必填欄位！');
                e.preventDefault();
                return;
            }

            const phonePattern = /^\d{8}$/;
            if (!phonePattern.test(phone.replace(/\s/g, ''))) {
                alert('請輸入8位數香港電話號碼');
                e.preventDefault();
                return;
            }
            alert('預約已提交！我們會盡快與你聯絡。');
        });
    }

    const dateInput = document.querySelector('input[name="booking_date"]');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
    }
});
