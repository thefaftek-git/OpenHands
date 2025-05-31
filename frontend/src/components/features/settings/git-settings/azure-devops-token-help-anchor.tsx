import { useTranslation } from "react-i18next";
import { I18nKey } from "#/i18n/declaration";

function TokenLink({ children }: { children: string }) {
  return (
    <a
      href="https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate"
      target="_blank"
      rel="noreferrer noopener"
      className="text-hyperlink underline"
    >
      {children}
    </a>
  );
}

function InstructionsLink({ children }: { children: string }) {
  return (
    <a
      href="https://docs.openhands.ai/modules/usage/how-to/use-git-providers#azure-devops"
      target="_blank"
      rel="noreferrer noopener"
      className="text-hyperlink underline"
    >
      {children}
    </a>
  );
}

export function AzureDevOpsTokenHelpAnchor() {
  const { t } = useTranslation();

  const tokenLinkRenderer = (chunks: string) => <TokenLink>{chunks}</TokenLink>;
  const instructionsLinkRenderer = (chunks: string) => (
    <InstructionsLink>{chunks}</InstructionsLink>
  );

  return (
    <div className="text-xs text-[#A3A3A3]">
      {t(I18nKey.AZURE_DEVOPS$TOKEN_HELP_TEXT, {
        0: tokenLinkRenderer,
        1: instructionsLinkRenderer,
      })}
    </div>
  );
}
