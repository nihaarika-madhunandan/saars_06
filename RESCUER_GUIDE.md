# 🚀 RESCUER SYSTEM GUIDE - How to Join and Start Rescuing

## 📌 Overview

The ResQPaws system now supports **THREE types of users**:

1. **Users/Reporters** - People who report injured/stray animals
2. **Rescuers** - People who rescue animals and help save lives
3. **Admins** - System administrators who manage everything

---

## ✅ How to Join as a Rescuer

### **Step 1: Go to Rescuer Signup**
- Visit the landing page at `http://localhost:5000/`
- Click on **"Join as Rescuer"** button
- OR go directly to: `http://localhost:5000/rescuer/signup`

### **Step 2: Fill Your Profile**
You'll need to provide:

#### **Personal Information:**
- **Full Name** - Your name
- **Email** - Your email address (used for login and notifications)
- **Phone Number** - Select your country code + enter your number
- **Service Location** - City/area where you rescue animals (e.g., "Delhi", "Mumbai")

#### **Rescue Experience:**
- **Your Experience & Skills** - Tell us about your animal rescue experience
  - Examples: "5 years of dog rescue experience", "Trained in wildlife handling", "Experienced with injured birds"
- **Certifications/Qualifications** (Optional)
  - Examples: "First Aid Certified", "Wildlife Handler", "Veterinary Assistant"

#### **Account Security:**
- **Password** - Min 8 characters, 1 uppercase letter, 1 number
- **Confirm Password** - Re-enter your password

### **Step 3: Create Account**
- Click **"Join as Rescuer"** button
- You'll get a confirmation email
- Login with your email and password

---

## 🎯 What Happens After You Join?

### **1. Welcome Email**
You'll receive an email with:
- Account confirmation
- Your profile details
- Instructions on what to do next

### **2. Access Rescuer Dashboard**
After login, you'll see:
- **Live Map** - Shows all animals needing rescue near you
- **Two Main Tabs:**
  - 🆘 **AWAITING RESCUE** - All pending animal cases you can claim
  - 🚀 **MY OPERATIONS** - Cases you've already claimed

### **3. Claim a Rescue Case**
1. Go to **AWAITING RESCUE** tab
2. Browse animals by:
   - Location
   - Animal type
   - Priority level (High/Medium/Low)
3. Click **"✅ CLAIM"** on an animal you want to rescue
4. The reporter gets notified that you're on the way
5. The case moves to **MY OPERATIONS** tab

### **4. Update Status**
In **MY OPERATIONS**, you can update status:
- ⏳ **Pending** - Initial state after claiming
- 🚀 **In Progress** - You're actively rescuing
- ✅ **Rescued** - Animal has been rescued!

When you mark as **"Rescued"**:
- Reporter gets a thank-you email
- Animal gets added to rescued count
- Your profile rating improves

### **5. Release a Case**
If you can't rescue a case, you can:
- Click **"❌ Release"** button
- The case goes back to AWAITING RESCUE
- Other rescuers can claim it

---

## 📊 Your Rescuer Profile

Each rescuer has:
- **Animals Rescued Count** - Total animals you've saved
- **Rating** - Community rating based on performance
- **Location** - Area of service
- **Experience** - Your qualifications and skills
- **Status** - Active rescuer badge

---

## 📧 Email Notifications You'll Get

### **1. When Someone Reports an Animal**
You get notifications if the animal is in your service area (based on your filters)

### **2. When You Claim a Case**
- Reporter receives: "Rescuer Claimed Your Report! 🚀" with your contact info

### **3. When You Mark as Rescued**
- Reporter receives: "Animal Rescued Successfully! 🎉" thank you email

### **4. Login Confirmation**
Every login sends you a security email

### **5. New Case Alerts**
Notifications about new animals matching your expertise

---

## 🔒 Account Security Tips

1. **Use a Strong Password** - Min 8 chars, mix uppercase and numbers
2. **Check Login Emails** - Monitor for suspicious activity
3. **Update Profile** - Keep your experience and location current
4. **Verify Before Claiming** - Read case details carefully

---

## 🚫 Account Types

### **Who Can Be a Rescuer?**
✅ **Anyone** who signs up through the rescuer signup page can become a rescuer!
- No background check required (can be added later)
- No approval process needed
- Immediate access to rescue cases

### **Admin-Only Addition**
🔐 Admins can also directly add rescuers through admin panel:
- `/admin/add-rescuer`
- Used for verified professionals
- Sends credentials via email

---

## 🆘 Troubleshooting

### **Q: I can't see MY OPERATIONS tab**
**A:** You need to claim at least one rescue case first. Go to AWAITING RESCUE and click CLAIM.

### **Q: Why don't I see any cases in AWAITING RESCUE?**
**A:** 
- No animals reported yet in the system, OR
- No animals match your service location, OR
- All available cases already claimed

### **Q: I claimed a case but it doesn't show in MY OPERATIONS**
**A:** Refresh the page. Check that rescuer_id is properly saved in database.

### **Q: I'm not getting emails**
**A:** Check:
- Email address is correct in your profile
- Check spam folder
- Verify email server is configured in app

### **Q: How do I change my password?**
**A:** Currently through admin. Request admin to reset or contact support.

---

## 📱 Mobile Friendly?

Yes! The rescuer dashboard is mobile-responsive:
- Access on phone or tablet
- Use map GPS for precise location
- Get case notifications on the go

---

## 🎓 Example Workflow

### **Day 1: Join ResQPaws**
1. Go to `http://localhost:5000/`
2. Click "Join as Rescuer"
3. Fill details (name, email, location: "Delhi", experience: "3 years dog rescue")
4. Create account
5. Verify email

### **Day 2: See Cases**
1. Login
2. Go to rescuer dashboard
3. Check "AWAITING RESCUE" tab
4. See 5 pending cases nearby

### **Day 3: Claim & Rescue**
1. Click CLAIM on a dog case
2. Reporter gets notified
3. Go to animal location
4. Rescue the animal
5. Update status to "Rescued"
6. Reporter gets thank-you email
7. Your rescued count increases

---

## 📞 Support

For issues or questions:
- Check email notifications
- Review your profile
- Contact admin
- Check this guide

---

## 🎉 You're Ready!

**Your account is now active. Start rescuing animals and save lives!**

Visit: `http://localhost:5000/login` and login to begin your rescue journey! 🐾
