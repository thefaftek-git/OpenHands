# Testing Instructions for Claude

## Core Testing Pattern
Always: Explore → Implement → Build → Run → Test in Browser → Verify

## Essential Commands

### Build and Start Application
```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start backend server  
cd openhands && poetry run uvicorn openhands.server.app:app --reload --host 0.0.0.0 --port 54341
```

### Test API Endpoints
```bash
curl http://localhost:54341/api/options/models | jq
```

### Browser Testing
- Navigate to http://localhost:54341/settings
- Test all dropdowns and functionality
- Check browser console for errors
- Verify API calls in network tab

## Quick Testing Checklist
- [ ] API returns expected data
- [ ] Frontend builds without errors
- [ ] Server starts successfully
- [ ] Settings page loads
- [ ] Dropdowns work correctly
- [ ] All options appear
- [ ] Selection works
- [ ] No console errors

## Add This to Any Prompt

**"After implementing this feature, please:**
1. **Build the frontend and start the backend server**
2. **Use the browser to navigate to the relevant page and test the functionality**
3. **Verify all dropdowns/components work correctly**
4. **Check for any console errors or API failures**
5. **Test edge cases and user interactions**
**Don't just implement - always run and test the actual application in the browser."**