defmodule HandlaBackend.Basket do
  use Agent, restart: :temporary

  @name __MODULE__

  def start_link(_opts) do
    Agent.start_link(fn -> %{} end, name: @name)
  end

  def get(key) do
    Agent.get(@name, &Map.get(&1, key, :checked))
  end

  def put(key, value \\ :unchecked) do
    Agent.update(@name, &Map.put(&1, key, value))
  end

  def delete(key) do
    Agent.get_and_update(@name, &Map.pop(&1, key))
  end
end
