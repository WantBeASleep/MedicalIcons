local modPath = ...

if not CLIENT then
    return
end

local morphineIdentifier = "antidama1"
local iconPath = modPath .. "/Items/Medical/Icons.png"
local iconSourceRect = Rectangle(192, 128, 64, 64)
local iconOrigin = Vector2(0.5, 0.5)
local spritePath = modPath .. "/Items/Medical/Sprites.png"
local spriteSourceRect = Rectangle(168, 0, 10, 65)
local spriteOrigin = Vector2(0.5, 0.5)
local spriteRotation = 0

local function getColor(name)
    if Color ~= nil then
        return Color[name]
    end

    return nil
end

local loggedPlainPrintFallback = false

local function logPlainPrintFallback(reason)
    if not loggedPlainPrintFallback then
        loggedPlainPrintFallback = true
        print("[Medical Icons] Falling back to plain print logging: " .. reason)
    end
end

local debugConsole = nil
local debugConsoleError = nil

local function getDebugConsole()
    if debugConsole ~= nil or debugConsoleError ~= nil then
        return debugConsole
    end

    local ok, result = pcall(function()
        return LuaUserData.CreateStatic("Barotrauma.DebugConsole")
    end)

    if ok then
        debugConsole = result
    else
        debugConsoleError = tostring(result)
    end

    return debugConsole
end

local function log(message, color)
    local text = "[Medical Icons] " .. message

    if color ~= nil then
        local console = getDebugConsole()

        if console ~= nil then
            local ok = pcall(function()
                console.NewMessage(text, color, false)
            end)

            if ok then
                return
            end

            local retryOk, retryResult = pcall(function()
                console.NewMessage(text, color)
            end)

            if retryOk then
                return
            end

            logPlainPrintFallback("DebugConsole.NewMessage failed: " .. tostring(retryResult))
        else
            logPlainPrintFallback("could not access Barotrauma.DebugConsole: " .. tostring(debugConsoleError))
        end
    else
        logPlainPrintFallback("color was not available")
    end

    print(text)
end

local function exposeSpriteInit()
    local ok, result = pcall(function()
        local spriteTypeName = "Barotrauma.Sprite"
        local spriteDescriptor = nil

        if LuaUserData.IsRegistered(spriteTypeName) then
            spriteDescriptor = LuaUserData[spriteTypeName]
            log("Reuse sprite descriptor", getColor("Cyan"))
        else
            spriteDescriptor = LuaUserData.RegisterType(spriteTypeName)
            log("Register sprite descriptor", getColor("Yellow"))
        end

        LuaUserData.MakeMethodAccessible(spriteDescriptor, "Init")
    end)

    if not ok then
        log("Could not expose Sprite.Init: " .. tostring(result), getColor("Red"))
    end
end

local function getMorphinePrefab()
    if Game ~= nil and Game.GetItemPrefab ~= nil then
        local prefab = Game.GetItemPrefab(morphineIdentifier)
        if prefab ~= nil then
            return prefab
        end
    end

    if ItemPrefab ~= nil and ItemPrefab.GetItemPrefab ~= nil then
        return ItemPrefab.GetItemPrefab(morphineIdentifier)
    end

    return nil
end

local prefab = getMorphinePrefab()

if prefab == nil then
    log("Morphine prefab not found: " .. morphineIdentifier, getColor("Red"))
    return
end

exposeSpriteInit()

local ok, result = pcall(function()
    prefab.InventoryIcon.Init(iconPath, iconSourceRect, iconOrigin, nil, 0)
end)

if ok then
    log("Reinitialized morphine inventory icon on client", getColor("Cyan"))
else
    log("Failed to reinitialize morphine inventory icon: " .. tostring(result), getColor("Red"))
end

ok, result = pcall(function()
    prefab.Sprite.Init(spritePath, spriteSourceRect, spriteOrigin, nil, spriteRotation)
    prefab.Sprite.Depth = 0.6
end)

if ok then
    log("Reinitialized morphine world sprite on client", getColor("Cyan"))
else
    log("Failed to reinitialize morphine world sprite: " .. tostring(result), getColor("Red"))
end


