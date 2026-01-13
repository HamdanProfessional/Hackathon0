# Personal AI Employee Vault

This is the **Obsidian vault** for your Personal AI Employee - your central command center.

## 📁 What is This?

This vault is the **memory and dashboard** for your AI Employee. It contains:
- Tasks and action items
- Approval workflows
- Business documentation
- System logs and briefings
- Financial tracking

## 🚀 How to Use

### Opening the Vault

1. **Install Obsidian** (if not already installed)
   - Download: https://obsidian.md/download

2. **Open This Folder as a Vault**
   - Open Obsidian
   - Click "Open folder as vault"
   - Select this `vault/` folder

3. **Start at the Dashboard**
   - Open `Dashboard.md` - your home base
   - Review pending tasks
   - Check system status

### Daily Workflow

```
1. Open Obsidian → Dashboard.md
2. Review Needs_Action/ folder
3. Process items:
   - Move urgent items to Pending_Approval/
   - Execute quick tasks manually
   - Delegate to AI Employee
4. Review Pending_Approval/
5. Move to Approved/ or Rejected/
6. Check Briefings/ for AI summaries
```

## 📂 Folder Structure

```
vault/
├── Dashboard.md              # Home base - start here!
├── Index.md                  # Complete documentation
├── Company_Handbook.md       # AI Employee rules
├── Business_Goals.md         # Your objectives
├── Needs_Action/             # Tasks detected by watchers
├── Approved/                 # Approved actions (AI executes)
├── Pending_Approval/         # Awaiting your review
├── Rejected/                 # Declined actions
├── Done/                     # Completed items
├── Briefings/                # Weekly CEO summaries
├── Logs/                     # System activity logs
├── Accounting/               # Financial tracking
├── Plans/                    # AI-generated plans
├── Inbox/                    # File drop zone
├── Templates/                # File templates
└── .obsidian/                # Obsidian settings
```

## ⚙️ Configuration

The vault works with the AI Employee system:

**Watchers** write TO this vault:
- Gmail Watcher → `Needs_Action/EMAIL_*.md`
- WhatsApp Watcher → `Needs_Action/WHATSAPP_*.md`
- File Watcher → `Needs_Action/FILE_*.md`

**Claude Code** reads FROM this vault:
- Reads `Needs_Action/` for tasks
- Consults `Company_Handbook.md` for rules
- Creates plans in `Plans/`
- Writes approval requests to `Pending_Approval/`

**You** approve IN this vault:
- Review `Pending_Approval/` items
- Move to `Approved/` to execute
- Move to `Rejected/` to cancel

**Approval Monitors** execute approvals:
- Watch `Approved/` folder
- Execute actions via MCP
- Log results to `Logs/`
- Move to `Done/`

## 🔒 Privacy

- ✅ All data stored **locally** on your machine
- ✅ No cloud sync by default
- ✅ No data sent to external services
- ✅ Encrypted at rest (with full disk encryption)
- ✅ Git-friendly for version control

## 📖 Documentation

- `Index.md` - Complete vault documentation
- `Dashboard.md` - Quick start guide
- `Company_Handbook.md` - How your AI behaves
- `Business_Goals.md` - Your targets and KPIs

## 🆘 Need Help?

### Troubleshooting
- See `Index.md` for troubleshooting guide
- Check project `README.md` (outside vault)
- Review `Logs/` for error details

### Common Issues

**"No items in Needs_Action"**
→ Watchers may not be running. Check: `pm2 list`

**"Items stuck in Pending_Approval"**
→ Open in Obsidian, review, move to Approved/ or Rejected/

**"Briefings not generating"**
→ Check cron schedule and Business_Goals.md exists

## 🎯 Best Practices

1. **Daily Check**: Review Dashboard.md (2 minutes)
2. **Weekly Review**: Audit Logs/ folder (15 minutes)
3. **Monthly**: Update Business_Goals.md
4. **Quarterly**: Full system review

## 📝 Notes

- This vault is designed for **human + AI collaboration**
- Edit any file to add context or correct AI decisions
- The AI learns from your approvals and rejections
- Keep Company_Handbook.md updated for best results

---

**Created:** 2026-01-11
**Version:** 1.0
**Status:** Active ✅
