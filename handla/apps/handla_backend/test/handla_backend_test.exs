defmodule HandlaBackendTest do
  use ExUnit.Case
  doctest HandlaBackend

  test "greets the world" do
    assert HandlaBackend.hello() == :world
  end
end
