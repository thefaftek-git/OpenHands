import React from "react";
import { useTranslation } from "react-i18next";
import { useSaveSettings } from "#/hooks/mutation/use-save-settings";
import { useSettings } from "#/hooks/query/use-settings";
import { BrandButton } from "#/components/features/settings/brand-button";
import { SettingsSwitch } from "#/components/features/settings/settings-switch";
import { SettingsInput } from "#/components/features/settings/settings-input";
import { I18nKey } from "#/i18n/declaration";
import {
  displayErrorToast,
  displaySuccessToast,
} from "#/utils/custom-toast-handlers";
import { retrieveAxiosErrorMessage } from "#/utils/retrieve-axios-error-message";
import { AppSettingsInputsSkeleton } from "#/components/features/settings/app-settings/app-settings-inputs-skeleton";

function AdditionalSettingsScreen() {
  const { t } = useTranslation();

  const { mutate: saveSettings, isPending } = useSaveSettings();
  const { data: settings, isLoading } = useSettings();

  const [coreSettings, setCoreSettings] = React.useState({
    debug: settings?.DEBUG || false,
    disable_color: settings?.DISABLE_COLOR || false,
    run_as_openhands: settings?.RUN_AS_OPENHANDS || true,
    enable_default_condenser: settings?.ENABLE_DEFAULT_CONDENSER || true,
  });

  const [llmSettings, setLlmSettings] = React.useState({
    drop_params: settings?.DROP_PARAMS || false,
    caching_prompt: settings?.CACHING_PROMPT || true,
    temperature: settings?.TEMPERATURE || 0.0,
    timeout: settings?.TIMEOUT || 0,
    top_p: settings?.TOP_P || 1.0,
    disable_vision: settings?.DISABLE_VISION || false,
  });

  const [agentSettings, setAgentSettings] = React.useState({
    function_calling: settings?.FUNCTION_CALLING || true,
    enable_llm_editor: settings?.ENABLE_LLM_EDITOR || false,
    enable_jupyter: settings?.ENABLE_JUPYTER || true,
    enable_history_truncation: settings?.ENABLE_HISTORY_TRUNCATION || true,
    enable_prompt_extensions: settings?.ENABLE_PROMPT_EXTENSIONS || true,
  });

  const [sandboxSettings, setSandboxSettings] = React.useState({
    timeout: settings?.SANDBOX_TIMEOUT || 120,
    user_id: settings?.SANDBOX_USER_ID || 1000,
    use_host_network: settings?.USE_HOST_NETWORK || false,
    enable_auto_lint: settings?.ENABLE_AUTO_LINT || false,
    initialize_plugins: settings?.INITIALIZE_PLUGINS || true,
  });

  const [securitySettings, setSecuritySettings] = React.useState({
    enable_security_analyzer: settings?.ENABLE_SECURITY_ANALYZER || false,
  });

  const handleCoreSettingsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setCoreSettings((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleLlmSettingsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setLlmSettings((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleAgentSettingsChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const { name, value, type, checked } = e.target;
    setAgentSettings((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSandboxSettingsChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const { name, value, type, checked } = e.target;
    setSandboxSettings((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSecuritySettingsChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const { name, value, type, checked } = e.target;
    setSecuritySettings((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const formAction = () => {
    saveSettings(
      {
        ...coreSettings,
        ...llmSettings,
        ...agentSettings,
        ...sandboxSettings,
        ...securitySettings,
      },
      {
        onSuccess: () => {
          displaySuccessToast(t(I18nKey.SETTINGS$SAVED));
        },
        onError: (error) => {
          const errorMessage = retrieveAxiosErrorMessage(error);
          displayErrorToast(errorMessage || t(I18nKey.ERROR$GENERIC));
        },
      },
    );
  };

  if (isLoading) {
    return <AppSettingsInputsSkeleton />;
  }

  return (
    <form
      data-testid="additional-settings-screen"
      action={formAction}
      className="flex flex-col h-full justify-between"
    >
      <div className="p-9 flex flex-col gap-6">
        <h2 className="text-xl font-bold">Core Settings</h2>
        <SettingsSwitch
          testId="debug-switch"
          name="debug"
          label={t(I18nKey.SETTINGS$DEBUG_MODE)}
          defaultIsToggled={coreSettings.debug}
          onToggle={handleCoreSettingsChange}
        />
        <SettingsSwitch
          testId="disable-color-switch"
          name="disable_color"
          label={t(I18nKey.SETTINGS$DISABLE_COLOR)}
          defaultIsToggled={coreSettings.disable_color}
          onToggle={handleCoreSettingsChange}
        />
        <SettingsSwitch
          testId="run-as-openhands-switch"
          name="run_as_openhands"
          label={t(I18nKey.SETTINGS$RUN_AS_OPENHANDS)}
          defaultIsToggled={coreSettings.run_as_openhands}
          onToggle={handleCoreSettingsChange}
        />
        <SettingsSwitch
          testId="enable-default-condenser-switch"
          name="enable_default_condenser"
          label={t(I18nKey.SETTINGS$ENABLE_DEFAULT_CONDENSER)}
          defaultIsToggled={coreSettings.enable_default_condenser}
          onToggle={handleCoreSettingsChange}
        />

        <h2 className="text-xl font-bold">LLM Settings</h2>
        <SettingsSwitch
          testId="drop-params-switch"
          name="drop_params"
          label={t(I18nKey.SETTINGS$DROP_PARAMS)}
          defaultIsToggled={llmSettings.drop_params}
          onToggle={handleLlmSettingsChange}
        />
        <SettingsSwitch
          testId="caching-prompt-switch"
          name="caching_prompt"
          label={t(I18nKey.SETTINGS$CACHING_PROMPT)}
          defaultIsToggled={llmSettings.caching_prompt}
          onToggle={handleLlmSettingsChange}
        />
        <SettingsInput
          testId="temperature-input"
          name="temperature"
          label={t(I18nKey.SETTINGS$TEMPERATURE)}
          defaultValue={llmSettings.temperature.toString()}
          type="number"
          onChange={handleLlmSettingsChange}
        />
        <SettingsInput
          testId="timeout-input"
          name="timeout"
          label={t(I18nKey.SETTINGS$TIMEOUT)}
          defaultValue={llmSettings.timeout.toString()}
          type="number"
          onChange={handleLlmSettingsChange}
        />
        <SettingsInput
          testId="top-p-input"
          name="top_p"
          label={t(I18nKey.SETTINGS$TOP_P)}
          defaultValue={llmSettings.top_p.toString()}
          type="number"
          onChange={handleLlmSettingsChange}
        />
        <SettingsSwitch
          testId="disable-vision-switch"
          name="disable_vision"
          label={t(I18nKey.SETTINGS$DISABLE_VISION)}
          defaultIsToggled={llmSettings.disable_vision}
          onToggle={handleLlmSettingsChange}
        />

        <h2 className="text-xl font-bold">Agent Settings</h2>
        <SettingsSwitch
          testId="function-calling-switch"
          name="function_calling"
          label={t(I18nKey.SETTINGS$FUNCTION_CALLING)}
          defaultIsToggled={agentSettings.function_calling}
          onToggle={handleAgentSettingsChange}
        />
        <SettingsSwitch
          testId="enable-llm-editor-switch"
          name="enable_llm_editor"
          label={t(I18nKey.SETTINGS$ENABLE_LLM_EDITOR)}
          defaultIsToggled={agentSettings.enable_llm_editor}
          onToggle={handleAgentSettingsChange}
        />
        <SettingsSwitch
          testId="enable-jupyter-switch"
          name="enable_jupyter"
          label={t(I18nKey.SETTINGS$ENABLE_JUPYTER)}
          defaultIsToggled={agentSettings.enable_jupyter}
          onToggle={handleAgentSettingsChange}
        />
        <SettingsSwitch
          testId="enable-history-truncation-switch"
          name="enable_history_truncation"
          label={t(I18nKey.SETTINGS$ENABLE_HISTORY_TRUNCATION)}
          defaultIsToggled={agentSettings.enable_history_truncation}
          onToggle={handleAgentSettingsChange}
        />
        <SettingsSwitch
          testId="enable-prompt-extensions-switch"
          name="enable_prompt_extensions"
          label={t(I18nKey.SETTINGS$ENABLE_PROMPT_EXTENSIONS)}
          defaultIsToggled={agentSettings.enable_prompt_extensions}
          onToggle={handleAgentSettingsChange}
        />

        <h2 className="text-xl font-bold">Sandbox Settings</h2>
        <SettingsInput
          testId="sandbox-timeout-input"
          name="timeout"
          label={t(I18nKey.SETTINGS$SANDBOX_TIMEOUT)}
          defaultValue={sandboxSettings.timeout.toString()}
          type="number"
          onChange={handleSandboxSettingsChange}
        />
        <SettingsInput
          testId="sandbox-user-id-input"
          name="user_id"
          label={t(I18nKey.SETTINGS$SANDBOX_USER_ID)}
          defaultValue={sandboxSettings.user_id.toString()}
          type="number"
          onChange={handleSandboxSettingsChange}
        />
        <SettingsSwitch
          testId="use-host-network-switch"
          name="use_host_network"
          label={t(I18nKey.SETTINGS$USE_HOST_NETWORK)}
          defaultIsToggled={sandboxSettings.use_host_network}
          onToggle={handleSandboxSettingsChange}
        />
        <SettingsSwitch
          testId="enable-auto-lint-switch"
          name="enable_auto_lint"
          label={t(I18nKey.SETTINGS$ENABLE_AUTO_LINT)}
          defaultIsToggled={sandboxSettings.enable_auto_lint}
          onToggle={handleSandboxSettingsChange}
        />
        <SettingsSwitch
          testId="initialize-plugins-switch"
          name="initialize_plugins"
          label={t(I18nKey.SETTINGS$INITIALIZE_PLUGINS)}
          defaultIsToggled={sandboxSettings.initialize_plugins}
          onToggle={handleSandboxSettingsChange}
        />

        <h2 className="text-xl font-bold">Security Settings</h2>
        <SettingsSwitch
          testId="enable-security-analyzer-switch"
          name="enable_security_analyzer"
          label={t(I18nKey.SETTINGS$ENABLE_SECURITY_ANALYZER)}
          defaultIsToggled={securitySettings.enable_security_analyzer}
          onToggle={handleSecuritySettingsChange}
        />
      </div>

      <div className="flex gap-6 p-6 justify-end border-t border-t-tertiary">
        <BrandButton
          testId="submit-button"
          type="submit"
          variant="primary"
          isDisabled={isPending}
        >
          {!isPending && t("SETTINGS$SAVE_CHANGES")}
          {isPending && t("SETTINGS$SAVING")}
        </BrandButton>
      </div>
    </form>
  );
}

export default AdditionalSettingsScreen;
