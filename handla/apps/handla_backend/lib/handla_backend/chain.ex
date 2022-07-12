defmodule HandlaBackend.Chain do
  use GenServer

  @moduledoc """
  Contains an event-source style chain of things that happen.

  Any interaction with the stateful modules should be done via the Chain.
  """

  @name __MODULE__

  def start_link(opts) do
    GenServer.start_link(@name, :ok, opts)
  end

  def add(thing) do
    GenServer.cast(@name, {:add, thing})
  end

  def remove(thing) do
    GenServer.cast(@name, {:remove, thing})
  end

  def comment(thing, comment) do
    GenServer.cast(@name, {:comment, thing, comment})
  end

  def add_thing(thing, category) do
    GenServer.cast(@name, {:thing_add, thing, category})
  end

  def remove_thing(thing) do
    GenServer.cast(@name, {:thing_remove, thing})
  end

  def add_category(key, name) do
    GenServer.cast(@name, {:category_add, key, name})
  end

  def remove_category(key) do
    GenServer.cast(@name, {:category_remove, key})
  end

  defp store(:nil, _command, _args), do: :ok

  defp store(fp, command, args) do
    letter = case command do
      :add -> 'a'
      :remove -> 'r'
      :comment -> 'c'
      :thing_add -> 't'
      :thing_remove -> 'h'
      :category_add -> 'y'
      :category_remove -> 'e'
    end
    IO.write(fp, ([letter | args] |> Enum.join("\t")) <> "\n")
  end

  defp parse_line(line) do
    line = line |> String.trim
    if String.starts_with?(line, "#") do
      :empty
    else
      case line do
        "" ->
          :empty
        line ->
          [letter | args] = line |> String.split("\t")
          [case letter do
            "a" -> :add
            "r" -> :remove
            "c" -> :comment
            "t" -> :thing_add
            "h" -> :thing_remove
            "y" -> :category_add
            "e" -> :category_remove
          end | args]
            |> List.to_tuple
      end
    end
  end

  defp read_chain(filename) do
    File.stream!(filename)
      |> Enum.map(&parse_line/1)
      |> Enum.filter(&is_not_empty?/1)
      |> Enum.each(&GenServer.cast(@name, &1))
  end

  defp is_not_empty?(:empty), do: false
  defp is_not_empty?(_result), do: true

  @impl true
  def init(:ok) do
    GenServer.cast(@name, {:open_for_read, "chain"})
    {:ok, :nil}
  end

  @impl true
  def handle_cast({:open_for_read, filename}, _fp) do
    require Logger
    Logger.debug("INIT, opening chain file '#{filename}' for read")
    read_chain(filename)
    GenServer.cast(@name, {:open_for_write, filename})
    {:noreply, :nil}
  end

  @impl true
  def handle_cast({:open_for_write, filename}, _fp) do
    require Logger
    Logger.debug("INIT, opening chain file '#{filename}' for write")
    {:noreply, File.open!(filename, [:append])}
  end

  @impl true
  def handle_cast({:add, thing}, fp) do
    :ok = HandlaBackend.Basket.put(thing)
    store(fp, :add, [thing])
    {:noreply, fp}
  end

  @impl true
  def handle_cast({:remove, thing}, fp) do
    HandlaBackend.Basket.delete(thing)
    store(fp, :remove, [thing])
    {:noreply, fp}
  end

  @impl true
  def handle_cast({:comment, thing, comment}, fp) do
    :ok = HandlaBackend.Basket.put(thing, comment)
    store(fp, :comment, [thing, comment])
    {:noreply, fp}
  end

  @impl true
  def handle_cast({:category_add, key, name}, fp) do
    :ok = HandlaBackend.Categories.put(key, name)
    store(fp, :category_add, [key, name])
    {:noreply, fp}
  end

  @impl true
  def handle_cast({:category_remove, key}, fp) do
    :ok = HandlaBackend.Categories.delete(key)
    store(fp, :category_remove, [key])
    {:noreply, fp}
  end

  @impl true
  def handle_cast({:thing_add, category, thing}, fp) do
    :ok = HandlaBackend.Things.put(thing, category)
    store(fp, :thing_add, [thing, category])
    {:noreply, fp}
  end

  @impl true
  def handle_cast({:thing_remove, thing}, fp) do
    :ok = HandlaBackend.Things.delete(thing)
    store(fp, :thing_remove, [thing])
    {:noreply, fp}
  end

  @impl true
  def handle_info({:DOWN, _ref, :process, _pid, _reason}, fp) do
    require Logger
    Logger.debug("Received a DOWN, closing chain file")
    File.close(fp)
    {:noreply, fp}
  end

  @impl true
  def handle_info(msg, fp) do
    require Logger
    Logger.debug("Unexpected message in HandlaBucket.Registry: #{inspect(msg)}")
    {:noreply, fp}
  end
end

