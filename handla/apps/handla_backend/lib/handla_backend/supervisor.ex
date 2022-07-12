defmodule HandlaBackend.Supervisor do
  use Supervisor

  def start_link(opts) do
    Supervisor.start_link(__MODULE__, :ok, opts)
  end

  @impl true
  def init(:ok) do
    if Mix.env() == :test do
      Supervisor.init([], strategy: :one_for_all)
    else
      children = [
        {HandlaBackend.Basket, name: HandlaBackend.Basket, strategy: :one_for_one},
        {HandlaBackend.Categories, name: HandlaBackend.Categories, strategy: :one_for_one},
        {HandlaBackend.Things, name: HandlaBackend.Things, strategy: :one_for_one},
        {HandlaBackend.Chain, name: HandlaBackend.Chain, strategy: :one_for_one}
      ]
      Supervisor.init(children, strategy: :one_for_all)
    end
  end
end
