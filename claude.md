# Claude Testing and Debugging Instructions

This document provides clear prompts and methodologies for testing and debugging OpenHands implementations, based on the successful litellm_proxy integration work.

## Core Testing Philosophy

When implementing features in OpenHands, always follow this pattern:
1. **Explore and understand** the existing codebase
2. **Implement** the minimal necessary changes
3. **Build and run** the application
4. **Test end-to-end** using the browser
5. **Verify** all functionality works as expected

## Essential Prompts for Testing

### 1. Initial Setup and Exploration
```
Please explore the OpenHands codebase to understand how [FEATURE] is currently implemented. Check both frontend and backend code, and identify what needs to be modified to implement [REQUIREMENT].
```

### 2. Building and Running the Application
```
Please build the frontend and start the backend server so I can test the implementation. Make sure to use the correct ports (54341 and 57779) and enable CORS/iframe support.
```

### 3. Browser Testing
```
Please use the browser to navigate to http://localhost:54341/settings and verify that [FEATURE] is working correctly. Test all dropdown options and functionality.
```

### 4. API Verification
```
Please verify the API endpoints are working correctly by testing /api/options/models and confirming the data structure matches frontend expectations.
```

## Specific Testing Methodology

### Frontend + Backend Integration Testing

1. **Start with API testing:**
   ```bash
   curl http://localhost:54341/api/options/models | jq
   ```

2. **Build frontend:**
   ```bash
   cd frontend && npm run build && cd ..
   ```

3. **Start backend:**
   ```bash
   cd openhands && poetry run uvicorn openhands.server.app:app --reload --host 0.0.0.0 --port 54341
   ```

4. **Test in browser:**
   - Navigate to settings page
   - Test dropdown functionality
   - Verify all options appear
   - Test selection and switching

### Browser Testing Checklist

When testing UI components, always verify:
- [ ] Dropdown opens correctly
- [ ] All expected options are present
- [ ] Options can be selected
- [ ] Selection persists
- [ ] No console errors
- [ ] API calls succeed

## Key Files to Check for Frontend Changes

### LLM Provider/Model Dropdowns
- `frontend/src/types/settings.ts` - Type definitions
- `frontend/src/services/settings.ts` - Default settings
- `frontend/src/hooks/query/use-settings.ts` - Settings query hook
- `frontend/src/hooks/mutation/use-save-settings.ts` - Settings mutation hook
- `frontend/src/routes/app-settings.tsx` - Settings UI components

### Backend Model Support
- `openhands/utils/llm.py` - Model definitions and API endpoints
- `openhands/server/listen.py` - API route definitions

## Debugging Patterns

### When UI Elements Don't Appear
1. Check browser developer tools for console errors
2. Verify API endpoints return expected data structure
3. Check if frontend components are properly mapped to backend data
4. Verify dropdown component accessibility tree

### When API Changes Don't Reflect
1. Restart backend server after code changes
2. Clear browser cache or hard refresh
3. Verify API response using curl or browser network tab
4. Check that frontend is calling the correct endpoint

### When Models/Options Missing
1. Verify backend function includes new models in return value
2. Check frontend mapping between API response and UI components
3. Ensure model names match exactly between frontend and backend
4. Verify no filtering is removing expected options

## Advanced Testing Prompts

### Full End-to-End Verification
```
Please perform a complete end-to-end test of the [FEATURE] implementation:
1. Start the backend server
2. Navigate to the settings page in browser
3. Test each dropdown option
4. Verify API calls are successful
5. Test model selection and switching
6. Confirm settings persistence
```

### Cross-Component Testing
```
Please verify that changes to [COMPONENT] don't break other parts of the application. Test the main conversation flow and other settings pages.
```

### Performance and Error Testing
```
Please test the implementation under various conditions:
- Network errors
- Invalid API responses  
- Edge cases with model selection
- Browser refresh scenarios
```

## Best Practices for Implementation

### Code Changes
- Make minimal, focused changes
- Always verify existing functionality still works
- Use consistent naming patterns
- Follow existing code structure

### Testing Approach
- Test incrementally as you implement
- Use browser developer tools actively
- Verify both happy path and edge cases
- Test on actual running application, not just unit tests

### Verification Steps
- Always run the actual application
- Use browser to test user-facing features
- Verify API endpoints with curl/network tools
- Check console for any errors or warnings

## Example Complete Testing Session

```
1. "Please explore how LLM providers are currently implemented in OpenHands"
2. "Please implement litellm_proxy support in the backend API"
3. "Please build the frontend and start the backend server"
4. "Please use the browser to test the settings page LLM Provider dropdown"
5. "Please verify all litellm_proxy models appear in the Model dropdown"
6. "Please test switching between different models"
7. "Please commit and push the changes"
```

This approach ensures thorough testing and catches integration issues early in the development process.