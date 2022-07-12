defmodule HandlaBackend.Categories do
  use Agent, restart: :temporary

  @name __MODULE__

  def start_link(_opts) do
    Agent.start_link(fn -> [] end, name: @name)
  end

  def get(key) do
    Agent.get(@name, &get_value_for_key(&1, key))
  end

  def put(key, name) do
    Agent.update(@name, &List.keystore(&1, key, 0, {key, name}))
  end

  def delete(key) do
    Agent.get_and_update(@name, &List.keydelete(&1, key, 0))
  end

  defp get_value_for_key(list, key) do
    case List.keyfind(list, key, 0) do
      {_key, name} -> name
      nil -> nil
    end
  end
end
