defmodule HandlaBackend do
  use Application

  @moduledoc """
  Provides the backend that handles the shopping lists and persists them to disk
  """

  @impl true
  def start(_type, _args) do
    HandlaBackend.Supervisor.start_link(name: HandlaBackend.Supervisor)
  end
end
