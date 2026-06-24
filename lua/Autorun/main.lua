if not CLIENT then return end

local modPath = ...
local log = require("limanchel.medical_icons.lib.logger")
log.Init("QoL - Medical Items", log.Levels.debug)

local data = require("limanchel.medical_icons.data")
local atlases = require("limanchel.medical_icons.generated.atlases")

-- expose sprite Init() method
local spriteDescriptor = LuaUserData["Barotrauma.Sprite"]
LuaUserData.MakeMethodAccessible(spriteDescriptor, "Init")

for identifier, item in pairs(atlases.items) do
    local prefab = Game.GetItemPrefab(identifier)

    -- skip wrong identifier
    if prefab == nil then
        log.Warn(string.format("Item prefab '%s' not found; skipping icon and sprite override", identifier))
        goto continue
    end

    ---@diagnostic disable-next-line: invisible // private Init expose earlier
    prefab.InventoryIcon.Init(modPath .. "/" .. atlases.assets.icons, Rectangle(table.unpack(item.icon.rect)),
        data.defaults.iconOrigin, nil, data.defaults.spriteRotation)

    ---@diagnostic disable-next-line: invisible // private Init expose earlier
    prefab.Sprite.Init(modPath .. "/" .. atlases.assets.sprites, Rectangle(table.unpack(item.sprite.rect)),
        data.defaults.spriteOrigin, nil, data.defaults.spriteRotation)
    prefab.Sprite.Depth = data.defaults.spriteDepth

    ::continue::
end

log.Info("Icons && Sprites successfully loaded!")
