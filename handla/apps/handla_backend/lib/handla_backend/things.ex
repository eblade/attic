defmodule HandlaBackend.Things do
  use Agent, restart: :temporary

  @name __MODULE__

  def start_link(_opts) do
    Agent.start_link(fn -> %{} end, name: @name)
  end

  def get_category(thing) do
    Agent.get(@name, &Map.get(&1, thing, :no_category))
  end

  def put(thing, category) do
    Agent.update(@name, &Map.put(&1, thing, category))
  end

  def delete(thing) do
    Agent.get_and_update(@name, &Map.pop(&1, thing))
  end
end
