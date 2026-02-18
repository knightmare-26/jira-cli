class JiraCli < Formula
  desc "LLM-Assisted Jira CLI"
  homepage "https://github.com/knightmare-26/jira-cli"
  url "https://github.com/knightmare-26/jira-cli/archive/refs/tags/v1.1.0.tar.gz"
  sha256 "05a2acaafff483a8c9cb7cf5fb974de978ef6381a1e671ee69bed387b982eb6c"

  depends_on "python@3.9"

  def install
    # Standard Homebrew Python installation pattern
    venv = virtualenv_create(libexec, "python3")
    venv.pip_install resources
    venv.pip_install_and_link buildpath
  end

  test do
    system "#{bin}/jira-cli", "--version"
  end
end