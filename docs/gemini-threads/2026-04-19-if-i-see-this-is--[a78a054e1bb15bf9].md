---
title: "If I see this, is the whole account basically dead?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "bdd1a72b-5e01-57e2-acd2-22cba6d81ed1"
url: ""
---

# If I see this, is the whole account basically dead?

> [!NOTE]
> Archived Gemini Thread: [If I see this, is the whole account basically dead?]() | Date: 2026-08-13

## User

If I see this, is the whole account basically dead?

---

## Gemini

Based on the screenshot, this specific page is blocked, but it doesn't necessarily mean the entire account is "dead." This "Access Denied" (FraudThrottle) message is a security measure triggered by Microsoft's automated systems.


Here is a breakdown of what is likely happening and how to address it:


What This Error Means
This error usually occurs when the system detects activity that looks like a violation of the Acceptable Use Policy. This could be triggered by:



* Sending a high volume of emails in a short window.

* Multiple failed login attempts.

* Accessing the account from an unusual location or via a suspicious VPN.

* Large-scale file sharing or downloading that triggers a "throttle."



Steps to Fix It
Before assuming the account is gone, try these steps in order:



* Wait it out: Sometimes these blocks are temporary (ranging from 1 to 24 hours). If it’s a "throttle," it may reset automatically.

* Clear Browser Cache: Try accessing the site via an Incognito/Private window or a different browser to rule out a localized session error.

* Check the Admin Center: If you have access to the Microsoft 365 Admin Center, check the Service Health dashboard or the Message Center. It will often specify if a specific user has been restricted.

* Contact Support: As the page suggests, if you are the administrator, you can open a support ticket through the Admin Center. If you are not the admin, you will need to contact your organization's IT department to have them unblock your specific user profile.



Is the Account "Dead"?
Likely no. In most cases, the data remains intact, but the access to it is suspended. Unless you have received a formal notification of a permanent account termination for legal or policy violations, this is usually a reversible security flag.


Are you the administrator for this account, or is this a personal/work login provided to you?

---

## User

my account has been restricted, I saw it in Sharepoint admin center before

---

## Gemini

Seeing that restriction in the SharePoint admin center confirms that this isn't just a random browser error—your account has been flagged at the tenant level.


Because you have access to the admin center, you aren't just a regular user; you have the tools to potentially see why this happened and clear it. Here is how to investigate and fix it:


1. Check for a "Blocked" Sign-in Status
Often, an "Acceptable Use Policy" flag will trigger a sign-in block on the user profile itself.



* Go to the Microsoft 365 Admin Center.

* Navigate to Users > Active users.

* Search for your account. Look for a status that says "Sign-in blocked" or a red icon.

* If it is blocked, click on the user and select Unblock sign-in.


2. Review the Service Health & Message Center
If Microsoft blocked the account for "Fraud" or "AUP" violations, they usually post a specific notice in your admin portal.



* In the Admin Center, go to Health > Service health.

* Check the Message center for any notices regarding "Malicious activity detected" or "Tenant restriction."


3. The "FraudThrottle" Specifics
The FraudThrottle.htm URL in your screenshot is a very specific "hard" block. Unlike standard throttling (which goes away in an hour), an AUP (Acceptable Use Policy) block usually requires manual intervention:



* If you are the Global Admin: You may need to verify your identity or your domain's intent. Go to the Support tab in the Admin Center and open a "New service request." Use the phrase "AUP Blocked SharePoint" in the description to get routed to the security team.

* Common Triggers: If this is a Developer E5 Sandbox or a new tenant, Microsoft's automated systems sometimes flag them if they see high-volume uploads, suspicious automated scripts, or if the account was recently created and immediately started heavy data movement.


Is it "Dead"?
If this is a paid production account, it is definitely not dead—support will restore it once you verify the activity. If this is a free Developer Sandbox (E5), Microsoft has been more aggressive recently with permanent bans for "policy violations" (often triggered by using sandboxes for personal storage rather than development).


Quick Question: Is this a standard work/business account, or is it one of the "Microsoft 365 Developer" sandbox accounts?

---

## User

> permanent bans for "policy violations" (often triggered by using sandboxes for personal storage rather than development
That's the camp I'm in, I've made my peace that this free ride is over, but I'm just wondering, should I delete this account or might it still be useful for something?

---

## Gemini

If you’ve accepted that the SharePoint/OneDrive "free ride" is over, the question of keeping the account depends on whether you value the Identity and Development features more than the Storage features.


Even with a SharePoint restriction, the account isn't necessarily a total loss. Here is how to weigh the decision:


Why You Might Keep It

* Entra ID (Active Directory) Testing: You can still use the account to learn how to manage users, groups, and security policies. It remains a powerful sandbox for learning the "Identity" side of IT administration.

* Power Platform: Often, these restrictions are specific to SharePoint/OneDrive. You might still be able to build apps in Power Apps or automations in Power Automate, provided they don't rely on SharePoint as a data source (you could use Dataverse or Excel instead).

* Graph API Practice: It’s still a valid endpoint for practicing API calls and learning how Microsoft’s backend architecture works.


Why You Should Consider Deleting It

* The "Flagged" Status: Once a tenant is flagged for AUP violations, it is difficult to ever get it back to "Good Standing." If you ever plan to do legitimate development later, it’s often better to start with a clean slate.

* Data Dead-End: Since the "FraudThrottle" block is active, you likely won't be able to use this account for any meaningful collaboration or file-sharing ever again.

* Security Hygiene: If you aren't using the admin features, there’s no reason to keep an active, global-admin-level account sitting idle.



If You Decide to Let It Go
Don't just walk away; close the tenant properly to ensure your custom domain (if you added one) and your identity are released from Microsoft’s system.



* Remove Custom Domains: If you linked a personal domain, remove it in the Microsoft 365 admin center under Settings > Domains so you can use it elsewhere.

* Cancel the Subscription: Even if it’s free, go to Billing > Your products and cancel the trial/subscription.

* Delete the Tenant: This is done via the Microsoft Entra ID (formerly Azure AD) portal. Under "Manage Tenants," you can select the tenant and click Delete.


One Final Check: Before you pull the plug, have you checked if you can still access the Exchange admin center? If email still works, the account might still have utility as a "burner" for testing mail flow or Outlook integrations.


Do you have any third-party apps or custom domains currently tied to this specific login?

---

## User

And I'm guessing since they're deactivating these accounts it's hard to get a new one?
How easily can one satisfy the developer usage thing but still use the storage for personal use?

---

## Gemini

You've hit on the exact reason why Microsoft has tightened the screws. In 2024 and 2025, Microsoft pivoted from a "loose" sign-up process to a very strict, tiered system because too many people were using these sandboxes as free 5TB cloud lockers rather than for actual coding.


1. How hard is it to get a new one?
It is significantly harder now. As of 2026, you can no longer simply sign up with a personal Outlook or Gmail address and get an E5 sandbox. To get a new one, you generally need to meet one of these "High-Bar" criteria:



* Visual Studio Subscription: You must have a paid Visual Studio Professional or Enterprise subscription.

* Microsoft Partner Status: Your company must be part of the ISV Success Program or the Microsoft AI Cloud Partner Program.

* Corporate/Education Identity: Even then, the system often triggers a "not eligible" message for individual users without a proven development history in the Microsoft ecosystem.



2. Can you still "mix" storage and development?
Technically, yes, but the "FraudThrottle" error you saw is proof that Microsoft’s AI is now specifically hunting for accounts that have high storage usage but zero API activity.


If you do manage to get a new account, here is how people are "satisfying" the developer requirements while still using the storage:



























StrategyWhat it looks like to MicrosoftComplexityMicrosoft Graph ActivitySetting up a script (e.g., via GitHub Actions) that makes periodic Microsoft Graph API calls to "read" or "update" a calendar or mail item.ModeratePower Automate FlowsCreating a few "useful" automations that run weekly (e.g., "Save email attachments to SharePoint"). This counts as developer activity.LowSample Data PacksInstalling the Sample Data Packs (User, Mail, and SharePoint data) from the Dev Dashboard. This populates the tenant with "test" data, making it look like a real dev environment.Very Low

The Reality Check: Even if you run these scripts, Microsoft’s Acceptable Use Policy explicitly states the E5 Sandbox is for "testing and development only." If they see 2TB of encrypted movie files or personal backups and only 10 API calls, the "FraudThrottle" will likely return.




Is there a better alternative?
If you just want the storage without the "Am I going to get banned today?" stress:



* Microsoft 365 Personal/Family: It often goes on sale for ~$50–$70/year and gives you a legitimate 1TB (or 6TB shared).

* Business Basic: For about $6/month, you get a "real" tenant with 1TB of OneDrive storage that Microsoft will never throttle for "lack of development" because you're a paying customer.


Since you've already seen the restriction, did you have a lot of data on that account that you still need to pull off, or are you starting from zero?

---

## User

my dad has a m365 account, and I've got 1tb of storage on my personal account as a result. That's the max I can get without paying?
I think the whole family pool is probably using like 50GB MAX. There's no way for him to allocate more of that storage to one account is there?

---

## Gemini

Since you are on a Microsoft 365 Family plan, you have hit the standard ceiling for a sub-account. Microsoft is quite rigid with these boundaries; they treat the "family pool" more like six individual lockers rather than one giant room with movable partitions.


Here is the breakdown of the storage logic and your options:


Can he reallocate the storage?
No. There is no "admin slider" that allows your dad to take unused space from other family members and give it to you. Each of the six slots is hard-coded to 1TB per person. Even if the other five people are using 0GB, your individual cap remains 1TB.



The "Standard" Max vs. The Paid Max
While 1TB is the max you get "for free" with the family invite, you actually can go higher, but it requires a monthly add-on fee. Microsoft allows the primary account holder (or the sub-accounts) to purchase additional storage in 200GB increments.



* The Cap: You can add up to an additional 1TB of storage on top of your base 1TB, bringing your personal total to 2TB.

* The Cost: Usually around $1.99/month per 200GB (prices vary slightly by region).



Is there a "Workaround"?
Since your family is only using 50GB of the remaining 5TB, you technically have a lot of "empty" real estate. While you can't merge it into one folder, here is how some people utilize the extra space:



* The "Split-Archive" Method: You could create a second Microsoft account, have your dad invite that "dummy" account to the family plan, and use its 1TB for long-term storage or backups (like photos or old projects). You would just have to log into that second account to access those specific files.

* Shared Folders: You can create a folder on one of the under-utilized accounts and "Share" it with your main account with Edit permissions. While this lets you see and move files from your main login, the files still "live" in the other account's quota.



Note: Be careful with the Shared Folder method for heavy syncing; OneDrive's sync engine can sometimes get finicky when handling massive shared directories across multiple accounts.



If you're already pushing that 1TB limit, are you mostly storing high-res media (photos/video) or is it a massive collection of smaller documents?

---

## User

If I paid for cloudmounter (or somehow found a pirated version) I could actually have that second account mounted pretty easily and take advantage of it...

---

## Gemini

That's a solid technical workaround. CloudMounter (or similar tools like Mountain Duck or RaiDrive) essentially treats cloud storage like a local hard drive, which makes managing a "split" 2TB much less of a headache than using the web interface.


If you go that route, here are a few things to keep in mind for a smooth setup:


Making the Most of the "Second Account"

* Selective Sync: Since you're essentially mounting 2TB of remote data, make sure you use the "Online-only" mode. This ensures the files only take up space on your actual hard drive when you open them.

* The "Pirated Version" Risk: Just a word of caution—since you’re dealing with your primary (and your dad’s) Microsoft credentials, using a "cracked" version of a mounting tool is risky. If that software is compromised, the "system" won't just see a policy violation; someone could actually gain access to your family's files or your dad's account.

* Performance: Mounted drives are usually slower than the native OneDrive client. It’s perfect for archives, movies, or backups, but I wouldn't recommend running active projects (like video editing or large databases) directly off the mount.



A "Clean" Alternative: The Shared Folder Hack
If you want to keep everything under one login without third-party software:



* Log into the "Dummy" account (Account B).

* Create a folder called "Big Storage" and Share it with your main account (Account A) with "Can Edit" permissions.

* On Account A, go to "Shared" in the sidebar and select "Add shortcut to My files."


Now, that 1TB folder from Account B appears inside your main OneDrive. You can move files into it, and they will count against Account B's quota, not yours. It’s basically "reallocating" the storage manually.


Final Note on the E5 Account
Since you're looking at the All admin centers page right now, if you decide to try and "save" that developer account one last time, your best bet is the Support tab to see if they'll give you a 48-hour window to move files. If not, the "Family Account" route is definitely the safer, more stable long-term play.


Does the "Shared Folder" trick sound like it would cover your needs, or do you definitely prefer having it show up as a separate drive letter?

---

