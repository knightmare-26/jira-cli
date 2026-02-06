class AiJiraCli < Formula
  desc "LLM-Assisted Jira CLI"
  homepage "https://github.com/knightmare-26/jira-cli"
  url "https://github.com/knightmare-26/jira-cli/archive/refs/tags/v1.0.3.tar.gz"
  sha256 "REPLACE_WITH_SHA256_CHECKSUM" # You need to replace this with the actual SHA256 checksum of the tarball

  depends_on "python@3.9"

  def install
    # Assuming your project is a Python package installable via pip
    # and has a 'jira-ai-cli' script in its entrypoints
    system "pip3", "install", *std_pip_args, "."
    bin.install "jira-ai-cli" => "ai-jira-cli"
  end

  test do
    # Basic test to ensure the CLI runs and shows help
    assert_match "Usage:", shell_output("#{bin}/ai-jira-cli --help")
  end
end