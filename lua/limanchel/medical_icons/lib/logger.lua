---@alias LoggerLevel integer

---@class LoggerLevels
---@field debug LoggerLevel
---@field info LoggerLevel
---@field warning LoggerLevel
---@field error LoggerLevel

---@type LoggerLevels
local level = {
    debug = 0,
    info = 1,
    warning = 2,
    error = 3,
}

---@type table<LoggerLevel, string>
local levelLabel = {
    [level.debug] = "DEBUG",
    [level.info] = "INFO",
    [level.warning] = "WARN",
    [level.error] = "ERROR",
}

---@class Logger
---@field private prefix string
---@field private level LoggerLevel
---@field private console Barotrauma.DebugConsole|nil
---@field Levels LoggerLevels
local logger = {
    prefix = "Logger",
    level = level.info,
    console = nil,
    Levels = level,
}

---Initializes the logger prefix, minimum visible level, and DebugConsole handle.
---@param prefix string
---@param minLevel LoggerLevel
---@return nil
function logger.Init(prefix, minLevel)
    logger.prefix = prefix
    logger.level = minLevel

    local ok, console = pcall(function()
        return LuaUserData.CreateStatic("Barotrauma.DebugConsole")
    end)

    if ok and console ~= nil then
        ---@diagnostic disable-next-line: assign-type-mismatch
        logger.console = console
    else
        logger.console = nil
        logger.Warn("DebugConsole initialization failed: " .. tostring(console))
    end
end

---@param message string
---@param messageLevel LoggerLevel
---@param color Microsoft.Xna.Framework.Color
---@private
---@return nil
function logger.log(message, messageLevel, color)
    local text = string.format("[%s][%s] %s", logger.prefix, levelLabel[messageLevel], message)

    if logger.console ~= nil then
        local ok, err = pcall(function()
            ---@diagnostic disable-next-line: invisible
            logger.console.NewMessage(text, color, false)
        end)

        if ok then return end

        print(string.format("[%s][%s] DebugConsole.NewMessage failed: %s; using print fallback",
            logger.prefix, levelLabel[level.error], tostring(err)))
    end

    print(text)
end

---Writes a debug message when the logger level allows it.
---@param message string
---@return nil
function logger.Debug(message)
    if logger.level > level.debug then return end

    logger.log(message, level.debug, Color.Green)
end

---Writes an informational message when the logger level allows it.
---@param message string
---@return nil
function logger.Info(message)
    if logger.level > level.info then return end

    logger.log(message, level.info, Color.Cyan)
end

---Writes a warning message when the logger level allows it.
---@param message string
---@return nil
function logger.Warn(message)
    if logger.level > level.warning then return end

    logger.log(message, level.warning, Color.Yellow)
end

---Writes an error message when the logger level allows it.
---@param message string
---@return nil
function logger.Error(message)
    if logger.level > level.error then return end

    logger.log(message, level.error, Color.Red)
end

---@return Logger logger
return logger
