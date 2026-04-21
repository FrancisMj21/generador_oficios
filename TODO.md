# Task: Fix form field issues - duplicate IDs, missing names, periods not saving to Supabase

## Plan Summary
- Fix duplicate IDs (selectAll, dynamic periods)
- Ensure periods serialize to hidden #periodos before submit
- Files: templates/index.html, static/app.js

## Steps to complete (mark with x when done)
- [x] Step 1: Edit templates/index.html ✅
  - Rename form selectAll → selectAllForm
  - Remove id/name from dynamic period fields
  - Add onsubmit="return updatePeriodos();" to form
- [x] Step 2: Edit static/app.js ✅
  - Add updatePeriodos() function to serialize periods
  - Hook updatePeriodos() to form onsubmit/DOM/add/remove/change/input
  - Added toggleTodosForm stub
- [ ] Step 3: Test form submission (periodos in POST body)
- [ ] Step 4: Verify no duplicate IDs, periods save to Supabase
- [ ] Step 5: attempt_completion

