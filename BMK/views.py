import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Neighborhood, Voter, Vote, Announcement, UserProfile

# --- RECAPTCHA KALITI ---
RECAPTCHA_SECRET_KEY = '6LexsJUsAAAAAHdNvnAWd_oSbSCy98yRgSSOu_c5'

# --- XABARLAR BILAN ISHLASH ---
def delete_announcement(request, pk):
    post = get_object_or_404(Announcement, pk=pk)
    post.delete()
    return redirect('mahallauz')

def mahallauz2(request):
    """Barcha xabarlarni eng yangisidan boshlab ko'rsatish"""
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'BMK/mahallauz2.html', {'announcements': announcements})


def mahallauz(request):
    """Xabarlar qo'shish va ko'rish (Admin/Rais uchun)"""
    announcements = Announcement.objects.all().order_by('-created_at')
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if title and content:
            Announcement.objects.create(
                title=title,
                content=content,
                image=image,
                video=video,
                author=request.user if request.user.is_authenticated else None
            )
            return redirect('mahallauz')
    return render(request, 'BMK/mahallauz.html', {'announcements': announcements})


def loyha(request):
    # 1. Barcha foydalanuvchilarni olamiz
    all_users = UserProfile.objects.all().order_by('full_name')

    # 2. Vote modelidan barcha ovoz bergan foydalanuvchilarning ID larini olamiz
    # (Agar 1-qadamni bajargan bo'lsangiz 'user_id' fieldi paydo bo'ladi)
    voted_user_ids = set(Vote.objects.values_list('user_id', flat=True))

    # 3. Har bir foydalanuvchiga 'voted' belgisini qo'shamiz
    for user in all_users:
        user.voted = user.id in voted_user_ids

    # 4. Statistikalar
    voted_count = len([u for u in all_users if user.voted])  # Ovoz berganlar soni
    total_users = all_users.count()
    not_voted_count = total_users - voted_count

    # Progress bar uchun (Maqsad 1000 ta ovoz deb olsak)
    goal = 1000
    progress = int((voted_count / goal) * 100) if goal > 0 else 0
    if progress > 100: progress = 100

    context = {
        'all_users': all_users,
        'voted_count': voted_count,
        'not_voted_count': not_voted_count,
        'total_users': total_users,
        'progress': progress,
        'goal': goal,
    }
    return render(request, 'BMK/loyha.html', context)
# --- LOGIN / REGISTER ---
def login(request):
    if request.session.get('temp_user'):
        return redirect('home')

    error_message = ""
    if request.method == "POST":
        u = request.POST.get('u_name', '').strip()
        p = request.POST.get('p_val', '').strip()
        d_id = request.POST.get('device_id')

        user = UserProfile.objects.filter(login__iexact=u, password=p).first()

        if user:
            if user.device_id and user.device_id != d_id:
                error_message = "Siz faqat ro'yxatdan o'tgan qurilmangizdan kira olasiz!"
            else:
                # Sessiyaga barcha kerakli ma'lumotlarni yozamiz
                request.session['temp_user'] = {
                    'full_name': user.full_name,
                    'mahalla_id': user.neighborhood.id if user.neighborhood else None,
                    'mahalla_name': user.neighborhood.name if user.neighborhood else user.mahalla,
                    'login': user.login,
                    'phone': user.phone
                }
                request.session.set_expiry(None)
                return redirect('home')
        else:
            error_message = "Login yoki parol xato!"
    return render(request, 'login.html', {'error_message': error_message})
def adminhomeee(request):
    user_data = request.session.get('temp_user')
    if not user_data:
        return redirect('login')
    return render(request, 'BMK/adminhome.html', {'user': user_data})

def home(request):
    user_data = request.session.get('temp_user')
    if not user_data:
        return redirect('login')
    return render(request, 'BMK/home.html', {'user': user_data})

def register(request):
    if request.session.get('temp_user'):
        return redirect('home')

    error_message = ""
    neighborhoods = Neighborhood.objects.all()

    if request.method == "POST":
        u = request.POST.get('u_name', '').strip()
        p = request.POST.get('p_val', '').strip()
        d_id = request.POST.get('device_id')
        n_id = request.POST.get('neighborhood')

        if UserProfile.objects.filter(device_id=d_id).exists():
            error_message = "Bu qurilmadan allaqachon ro'yxatdan o'tilgan!"
        elif UserProfile.objects.filter(login__iexact=u).exists():
            error_message = "Bu login band!"
        else:
            # Mahalla obyektini olish
            neighborhood = Neighborhood.objects.filter(id=n_id).first()
            user = UserProfile.objects.create(
                full_name=request.POST.get('full_name'),
                login=u,
                password=p,
                phone=request.POST.get('phone'),
                neighborhood=neighborhood,
                mahalla=neighborhood.name if neighborhood else "",
                device_id=d_id
            )
            request.session['temp_user'] = {
                'full_name': user.full_name,
                'mahalla_id': neighborhood.id if neighborhood else None,
                'mahalla_name': neighborhood.name if neighborhood else "",
                'login': user.login,
                'phone': user.phone
            }
            request.session.set_expiry(None)
            return redirect('home')

    return render(request, 'register.html', {'error_message': error_message, 'neighborhoods': neighborhoods})

# --- OVOZ BERISH JARAYONI ---
def vote_view(request):
    """reCAPTCHA bilan kengaytirilgan ovoz berish"""
    user_data = request.session.get('temp_user')
    if not user_data:
        return redirect('login')

    step = request.session.get('step', 'phone')
    phone_number = request.session.get('phone_number', user_data.get('phone', ''))

    if request.method == 'POST':
        if 'send_sms' in request.POST:
            phone = request.POST.get('phone')
            recaptcha_response = request.POST.get('g-recaptcha-response')

            # reCAPTCHA tekshiruvi
            verify_data = {'secret': RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
            verify_rs = requests.post('https://www.google.com/recaptcha/api/siteverify', data=verify_data)
            if not verify_rs.json().get('success'):
                messages.error(request, "Iltimos, robot emasligingizni tasdiqlang!")
                return render(request, 'BMK/vote.html', {'step': 'phone', 'phone_number': phone})

            request.session['phone_number'] = phone
            request.session['step'] = 'verify'
            messages.success(request, "Kod telefoningizga yuborildi.")
            return redirect('sms_send') # URL nomi urls.py dagi nomga mos bo'lishi kerak

        elif 'verify_code' in request.POST:
            sms_code = request.POST.get('sms_code')
            if sms_code == '123456': # Test uchun kod
                return verify_and_finish(request)
            else:
                messages.error(request, "Xato kod kiritildi.")
                return render(request, 'BMK/vote.html', {'step': 'verify', 'phone_number': phone_number})

    return render(request, 'BMK/vote.html', {'step': step, 'phone_number': phone_number})

def verify_and_finish(request):
    """Ovozni bazada yakunlash va Rahmat sahifasiga o'tish"""
    user_data = request.session.get('temp_user')
    n_id = user_data.get('mahalla_id')

    try:
        neighborhood = get_object_or_404(Neighborhood, id=n_id)
        neighborhood.votes_count += 1
        neighborhood.save()

        # Voter va Vote modellariga yozish
        Voter.objects.create(
            first_name=user_data.get('full_name'),
            phone=request.session.get('phone_number'),
            neighborhood=neighborhood,
            is_voted=True
        )
        Vote.objects.create(neighborhood=neighborhood)

        request.session['step'] = 'phone' # Qayta kirganda noldan boshlash uchun
        return render(request, 'BMK/success.html', {'first_name': user_data['full_name']})
    except Exception as e:
        messages.error(request, "Xatolik yuz berdi!")
        return redirect('home')