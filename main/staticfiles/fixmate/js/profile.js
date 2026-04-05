// Profile Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Переключение вкладок
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`${tabId}Tab`).classList.add('active');
        });
    });

    // Модальное окно редактирования профиля
    const modal = document.getElementById('editProfileModal');
    const openBtn = document.getElementById('openEditModalBtn');
    const closeBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelModalBtn');

    openBtn.addEventListener('click', () => {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Загрузка аватара
    const uploadAvatarBtn = document.getElementById('uploadAvatarBtn');
    const avatarUpload = document.getElementById('avatarUpload');
    const currentAvatarPreview = document.getElementById('currentAvatarPreview');
    const removeAvatarBtn = document.getElementById('removeAvatarBtn');

    uploadAvatarBtn.addEventListener('click', () => {
        avatarUpload.click();
    });

    avatarUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                currentAvatarPreview.innerHTML = `<img src="${event.target.result}" alt="Аватар">`;
                removeAvatarBtn.style.display = 'inline-block';
            };
            reader.readAsDataURL(file);
        }
    });

    removeAvatarBtn.addEventListener('click', () => {
        currentAvatarPreview.innerHTML = `<div class="default-avatar-preview">${getInitials()}</div>`;
        avatarUpload.value = '';
        removeAvatarBtn.style.display = 'none';
    });

    function getInitials() {
        const name = document.getElementById('editDisplayName').value;
        return name.charAt(0).toUpperCase();
    }

    // Сохранение формы (имитация)
    const profileForm = document.querySelector('.edit-profile-form');
    const toast = document.getElementById('toastNotification');

    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Здесь будет отправка на сервер
        const formData = new FormData(profileForm);

        // Обновляем отображаемые данные
        const newName = document.getElementById('editDisplayName').value;
        const newBio = document.getElementById('editBio').value;

        document.getElementById('profileName').textContent = newName;
        document.getElementById('profileBio').textContent = newBio || 'Разработчик, изучающий программирование с AI';

        // Показываем уведомление
        showToast('Профиль успешно обновлен!');
        closeModal();
    });

    function showToast(message) {
        toast.querySelector('.toast-message').textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Настройки (сохранение в localStorage)
    const emailNotifications = document.getElementById('emailNotifications');
    const publicProfile = document.getElementById('publicProfile');
    const darkTheme = document.getElementById('darkTheme');
    const aiTips = document.getElementById('aiTips');

    function loadSettings() {
        emailNotifications.checked = localStorage.getItem('emailNotifications') === 'true';
        publicProfile.checked = localStorage.getItem('publicProfile') === 'true';
        darkTheme.checked = localStorage.getItem('darkTheme') === 'true';
        aiTips.checked = localStorage.getItem('aiTips') === 'true';

        if (darkTheme.checked) {
            document.body.classList.add('dark-theme');
        }
    }

    function saveSettings() {
        localStorage.setItem('emailNotifications', emailNotifications.checked);
        localStorage.setItem('publicProfile', publicProfile.checked);
        localStorage.setItem('darkTheme', darkTheme.checked);
        localStorage.setItem('aiTips', aiTips.checked);

        if (darkTheme.checked) {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }

        showToast('Настройки сохранены');
    }

    emailNotifications.addEventListener('change', saveSettings);
    publicProfile.addEventListener('change', saveSettings);
    darkTheme.addEventListener('change', saveSettings);
    aiTips.addEventListener('change', saveSettings);

    loadSettings();

    // Редактирование аватара через кнопку на аватаре
    const editAvatarBtn = document.getElementById('editAvatarBtn');
    editAvatarBtn.addEventListener('click', () => {
        openModalAndFocusAvatar();
    });

    function openModalAndFocusAvatar() {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        setTimeout(() => {
            uploadAvatarBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    }

    // Мобильное меню
    const mobileMenuBtn = document.createElement('button');
    mobileMenuBtn.innerHTML = '☰';
    mobileMenuBtn.className = 'mobile-menu-btn';
    mobileMenuBtn.style.cssText = `
        position: fixed;
        top: 16px;
        left: 16px;
        z-index: 1000;
        background: rgba(102, 126, 234, 0.9);
        border: none;
        color: white;
        font-size: 24px;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        cursor: pointer;
        display: none;
    `;
    document.body.appendChild(mobileMenuBtn);

    const sidebar = document.querySelector('.sidebar');

    function checkMobile() {
        if (window.innerWidth <= 768) {
            mobileMenuBtn.style.display = 'block';
            sidebar.classList.remove('open');
        } else {
            mobileMenuBtn.style.display = 'none';
            sidebar.classList.remove('open');
        }
    }

    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    window.addEventListener('resize', checkMobile);
    checkMobile();
});